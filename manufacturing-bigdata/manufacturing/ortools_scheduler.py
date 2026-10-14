"""Optional CP-SAT scheduler. Called by the engine only when OR-Tools is installed."""
from datetime import datetime, timedelta
import math


def build_schedule_cp_sat(requirements, machines=None, products=None, failures=None, hours=8, start=None):
    from ortools.sat.python import cp_model
    from manufacturing.engine import MACHINES as DEFAULT_MACHINES, PRODUCTS as DEFAULT_PRODUCTS
    machines=[dict(m) for m in (machines or DEFAULT_MACHINES)]
    product_map=products or {p['product_id']:p for p in DEFAULT_PRODUCTS}
    failed=set(failures or [])
    machines=[m for m in machines if m.get('available',True) and m['machine_id'] not in failed]
    horizon=int(hours*60); model=cp_model.CpModel(); placements={}; intervals={m['machine_id']:[] for m in machines}; unsatisfied=[]
    for idx, req in enumerate(requirements):
        pid=req['product_id']; requested=max(0,int(req.get('quantity',0)))
        if requested==0 or pid not in product_map: continue
        product=product_map[pid]; material=float(req.get('material_available',float('inf')))
        if math.isfinite(material): requested=min(requested,max(0,int(material/max(float(product['material_per_unit']),1e-9))))
        assigned=[]
        for m_idx,machine in enumerate(machines):
            if pid not in machine['supported_products']: continue
            key=(idx,machine['machine_id']); rate_x100=max(1,round(float(machine['capacity_units_per_hour'])*float(machine['efficiency'])*100))
            qty=model.NewIntVar(0,requested,f'q_{idx}_{m_idx}'); present=model.NewBoolVar(f'use_{idx}_{m_idx}')
            duration=model.NewIntVar(0,horizon,f'duration_{idx}_{m_idx}'); st=model.NewIntVar(0,horizon,f'start_{idx}_{m_idx}'); end=model.NewIntVar(0,horizon,f'end_{idx}_{m_idx}')
            model.Add(qty<=requested*present); model.Add(qty>=present)
            setup=int(product['setup_time_minutes'])
            model.Add(duration*rate_x100 >= 6000*qty + setup*rate_x100*present)
            model.Add(duration<=horizon*present); model.Add(st<=horizon*present); model.Add(end<=horizon*present)
            model.Add(end==st+duration)
            interval=model.NewOptionalIntervalVar(st,duration,end,present,f'interval_{idx}_{m_idx}')
            intervals[machine['machine_id']].append(interval)
            assigned.append(qty); placements[key]=(qty,present,st,end,duration,machine,req)
        short=model.NewIntVar(0,requested,f'unserved_{idx}')
        unsatisfied.append((short,req))
        if assigned: model.Add(sum(assigned)+short==requested)
        else: model.Add(short==requested)
    for ivals in intervals.values():
        if ivals: model.AddNoOverlap(ivals)
    objective=[]
    for short,req in unsatisfied:
        objective.append(100000*max(1,int(req.get('priority_weight',1)))*short)
    for qty,present,st,end,duration,machine,req in placements.values():
        cost=int(round(float(machine.get('operating_cost_per_hour',1))))
        prio=max(1,int(req.get('priority_weight',1)))
        objective.extend([cost*duration, max(1,100//prio)*st, 10*present])
    if objective: model.Minimize(sum(objective))
    solver=cp_model.CpSolver(); solver.parameters.max_time_in_seconds=2.0; solver.parameters.num_search_workers=4
    status=solver.Solve(model)
    if status not in (cp_model.OPTIMAL,cp_model.FEASIBLE):
        raise RuntimeError('CP-SAT did not find a feasible schedule')
    start=start or datetime.now().replace(hour=8,minute=0,second=0,microsecond=0)
    jobs=[]
    for (idx,machine_id),(qty,present,st,end,duration,machine,req) in placements.items():
        amount=solver.Value(qty)
        if amount<=0: continue
        start_dt=start+timedelta(minutes=solver.Value(st)); end_dt=start+timedelta(minutes=solver.Value(end))
        jobs.append({'job_id':f'J{len(jobs)+1:04}','product_id':req['product_id'],'machine_id':machine_id,'quantity':amount,'start_time':start_dt.isoformat(),'end_time':end_dt.isoformat(),'duration_minutes':solver.Value(duration),'priority':req.get('priority','NORMAL'),'status':'SCHEDULED'})
    jobs.sort(key=lambda job:(job['machine_id'],job['start_time']))
    return jobs
