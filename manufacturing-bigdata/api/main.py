from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from manufacturing.engine import PRODUCTS,MACHINES,INVENTORY,forecast,event_adjustment,requirement,build_schedule,kpis

app=FastAPI(title='Demand-Driven Smart Manufacturing Prototype',version='0.1.0')
state={'failures':set(),'events':[],'demand_multiplier':1.0,'schedule':[]}
class Failure(BaseModel): machine_id:str
class Scenario(BaseModel): demand_change_pct:float=0; failed_machines:list[str]=[]; inventory_adjustment:dict[str,int]={}
class NewsEvent(BaseModel): event_type:str='market'; affected_products:list[str]=[]; demand_direction:str='neutral'; supply_direction:str='neutral'; severity:str='low'; relevance_score:float=Field(default=0,ge=0,le=1); confidence:float=Field(default=0,ge=0,le=1); summary:str=''; source_url:str=''

def get_forecasts(mult=1.0):
    histories={'P001':[70,68,75,80,72,84,88,90,85,92,94,100,98,104],'P002':[40,45,42,47,50,54,51,56,59,58,61,65,63,68],'P003':[22,20,24,25,27,26,29,30,31,33,30,35,36,38],'P004':[52,53,54,50,58,59,61,62,64,63,67,68,70,72],'P005':[31,30,35,34,37,38,40,41,43,42,45,46,48,49]}
    adjustments={p:0.0 for p in histories}
    for e in state['events']:
        adj=event_adjustment(e)
        for p in e.get('affected_products',[]) or histories: adjustments[p]=max(-.25,min(.25,adjustments.get(p,0)+adj))
    return forecast(histories,7,adjustments)

def requirements_for(mult=1.0, inv_adjust=None):
    inv_adjust=inv_adjust or {}; result=[]
    for f in get_forecasts(mult):
        inv=dict(INVENTORY[f['product_id']]); inv['current_stock']=max(0,inv['current_stock']+int(inv_adjust.get(f['product_id'],0)))
        need=requirement(f['horizon_units']*mult,inv)
        result.append({'product_id':f['product_id'],'quantity':need,'priority':'HIGH' if need>500 else 'NORMAL','priority_weight':2 if need>500 else 1})
    return result
@app.get('/health')
def health(): return {'status':'ok','mode':'prototype','live_llm_enabled':False}
@app.get('/products')
def products(): return PRODUCTS
@app.get('/machines')
def machines(): return [dict(m,available=m['machine_id'] not in state['failures']) for m in MACHINES]
@app.get('/inventory')
def inventory(): return INVENTORY
@app.get('/forecast')
def forecasts(): return get_forecasts()
@app.get('/production-requirements')
def production_requirements(): return requirements_for()
@app.get('/schedule')
def schedule():
    if not state['schedule']: state['schedule']=build_schedule(requirements_for(),failures=state['failures'])
    return state['schedule']
@app.get('/kpis')
def get_kpis():
    req=requirements_for(); jobs=build_schedule(req,failures=state['failures']); return kpis(jobs,req)
@app.get('/news-impact')
def news(): return state['events']
@app.post('/news-events')
def add_news(event:NewsEvent):
    record=event.model_dump(); record['affected_products']=record['affected_products'] or (['P001','P002'] if 'manufactur' in record['summary'].lower() or 'electronics' in record['summary'].lower() else [])
    record['event_adjustment_pct']=round(event_adjustment(record),4); state['events'].append(record); state['schedule']=[]; return record
@app.post('/simulate/machine-failure')
def fail_machine(event:Failure):
    if event.machine_id not in {m['machine_id'] for m in MACHINES}: raise HTTPException(404,'Unknown machine')
    state['failures'].add(event.machine_id); req=requirements_for(); old=state['schedule']; state['schedule']=build_schedule(req,failures=state['failures']); return {'failed_machine':event.machine_id,'schedule':state['schedule'],'kpis':kpis(state['schedule'],req),'rescheduled':True,'previous_job_count':len(old)}
@app.post('/reschedule')
def reschedule():
    req=requirements_for(); state['schedule']=build_schedule(req,failures=state['failures']); return {'schedule':state['schedule'],'kpis':kpis(state['schedule'],req)}
@app.post('/simulate/scenario')
def scenario(s:Scenario):
    mult=max(.5,min(1.5,1+s.demand_change_pct/100)); req=requirements_for(mult=mult,inv_adjust=s.inventory_adjustment); fails=set(s.failed_machines); jobs=build_schedule(req,failures=fails); return {'scenario':s.model_dump(),'requirements':req,'schedule':jobs,'kpis':kpis(jobs,req)}
