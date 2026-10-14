"""Core deterministic forecasting, requirements and simple constraint-aware schedule."""
from datetime import datetime, timedelta
import math

PRODUCTS=[{'product_id':'P001','product_name':'Drive Module','category':'ELECTRONICS','processing_time_minutes':42,'setup_time_minutes':18,'required_material':'copper','material_per_unit':2.0}, {'product_id':'P002','product_name':'Control Unit','category':'ELECTRONICS','processing_time_minutes':35,'setup_time_minutes':15,'required_material':'circuit_board','material_per_unit':1.0}, {'product_id':'P003','product_name':'Pump Assembly','category':'MECHANICAL','processing_time_minutes':55,'setup_time_minutes':22,'required_material':'steel','material_per_unit':4.5}, {'product_id':'P004','product_name':'Sensor Pack','category':'ELECTRONICS','processing_time_minutes':24,'setup_time_minutes':12,'required_material':'silicon','material_per_unit':.4}, {'product_id':'P005','product_name':'Valve Kit','category':'MECHANICAL','processing_time_minutes':30,'setup_time_minutes':16,'required_material':'aluminum','material_per_unit':1.8}]
MACHINES=[{'machine_id':'M001','machine_type':'CNC','capacity_units_per_hour':70,'efficiency':.92,'operating_cost_per_hour':48,'supported_products':['P001','P003','P005'],'available':True},{'machine_id':'M002','machine_type':'ASSEMBLY','capacity_units_per_hour':90,'efficiency':.88,'operating_cost_per_hour':35,'supported_products':['P001','P002','P004'],'available':True},{'machine_id':'M003','machine_type':'ELECTRONICS','capacity_units_per_hour':110,'efficiency':.95,'operating_cost_per_hour':42,'supported_products':['P002','P004','P005'],'available':True},{'machine_id':'M004','machine_type':'MIXED','capacity_units_per_hour':55,'efficiency':.84,'operating_cost_per_hour':30,'supported_products':['P001','P003','P004'],'available':True}]
INVENTORY={product_id:{'current_stock':stock,'safety_stock':100,'reserved_quantity':reserved,'incoming_quantity':incoming} for product_id,stock,reserved,incoming in [('P001',210,30,0),('P002',90,10,60),('P003',330,25,0),('P004',140,10,80),('P005',170,20,0)]}

def moving_average(history, window=7):
    values=[float(x) for x in history]
    if not values: return 0.0
    return max(0.0, sum(values[-window:])/min(window,len(values)))

def forecast(history_by_product, days=7, event_adjustments=None):
    event_adjustments=event_adjustments or {}; out=[]
    for product, history in history_by_product.items():
        base=moving_average(history)
        pct=max(-.25,min(.25,float(event_adjustments.get(product,0))))
        out.append({'product_id':product,'baseline_daily':round(base,2),'event_adjustment_pct':round(pct,4),'final_daily':round(base*(1+pct),2),'horizon_units':round(base*(1+pct)*days,2),'horizon_days':days})
    return out

def event_adjustment(event):
    """Calibrated rule; LLM classifications can only supply bounded categorical inputs."""
    if event.get('demand_direction') not in ('positive','negative'): return 0.0
    severity={'low':.02,'medium':.05,'high':.08,'critical':.12}.get(str(event.get('severity','low')).lower(),0.0)
    relevance=max(0,min(1,float(event.get('relevance_score',0))))
    confidence=max(0,min(1,float(event.get('confidence',0))))
    sign=1 if event['demand_direction']=='positive' else -1
    return sign*severity*relevance*confidence

def requirement(forecast_units, inventory, planned=0):
    available=max(0,float(inventory.get('current_stock',0))-float(inventory.get('reserved_quantity',0)))
    incoming=float(inventory.get('incoming_quantity',0))
    target=float(forecast_units)+float(inventory.get('safety_stock',0))
    return max(0,math.ceil(target-available-incoming-float(planned)))

def build_schedule(requirements, machines=None, products=None, failures=None, hours=8, start=None):
    """Greedy feasible demo scheduler: compatibility, capacity, material cap and no overlap per machine."""
    try:
        from manufacturing.ortools_scheduler import build_schedule_cp_sat
        return build_schedule_cp_sat(requirements, machines, products, failures, hours, start)
    except ImportError:
        pass
    machines=machines or [dict(m) for m in MACHINES]; products=products or {p['product_id']:p for p in PRODUCTS}; failures=set(failures or [])
    for m in machines: m['available']=m.get('available',True) and m['machine_id'] not in failures
    cursor={m['machine_id']:0 for m in machines}; jobs=[]; start=start or datetime.now().replace(hour=8,minute=0,second=0,microsecond=0)
    ordered=sorted(requirements,key=lambda r:(-int(r.get('priority_weight',1)),r['product_id']))
    for req in ordered:
        pid=req['product_id']; qty=max(0,int(req.get('quantity',0)))
        if qty==0 or pid not in products: continue
        p=products[pid]; material_qty=float(req.get('material_available',float('inf'))); material_limit=qty if material_qty==float('inf') else int(material_qty/max(float(p['material_per_unit']),1e-9)); remaining=min(qty,material_limit)
        while remaining>0:
            choices=[m for m in machines if m.get('available') and pid in m['supported_products'] and cursor[m['machine_id']]<hours*60]
            if not choices: break
            m=min(choices,key=lambda x:cursor[x['machine_id']]+(float(p['processing_time_minutes'])/max(1,x['capacity_units_per_hour']*60*x['efficiency']))*60)
            rate=max(1,float(m['capacity_units_per_hour'])*float(m['efficiency']))
            fit=int(max(0,(hours*60-cursor[m['machine_id']]-float(p['setup_time_minutes']))*rate/60))
            if fit<=0: m['available']=False; continue
            count=min(remaining,fit); duration=float(p['setup_time_minutes'])+count*60/rate
            st=start+timedelta(minutes=cursor[m['machine_id']]); en=st+timedelta(minutes=duration)
            jobs.append({'job_id':f'J{len(jobs)+1:04}','product_id':pid,'machine_id':m['machine_id'],'quantity':count,'start_time':st.isoformat(),'end_time':en.isoformat(),'duration_minutes':round(duration,1),'priority':req.get('priority','NORMAL'),'status':'SCHEDULED'})
            cursor[m['machine_id']]+=math.ceil(duration); remaining-=count
            if remaining and cursor[m['machine_id']]>=hours*60: m['available']=False
    return jobs

def kpis(schedule, requirements):
    units=sum(j['quantity'] for j in schedule); requested=sum(max(0,int(x.get('quantity',0))) for x in requirements)
    active={j['machine_id'] for j in schedule}; return {'required_units':requested,'scheduled_units':units,'unscheduled_units':max(0,requested-units),'completion_rate':round(units/requested,4) if requested else 1.0,'machines_used':len(active),'schedule_jobs':len(schedule)}
