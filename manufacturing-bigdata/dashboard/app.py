import os, requests, streamlit as st
API=os.getenv('API_BASE_URL','http://localhost:8000')
st.set_page_config(page_title='Smart Manufacturing',layout='wide')
st.title('Demand-Driven Smart Manufacturing')
st.caption('Prototype • synthetic operational data • event adjustments are deterministic and capped')
def get(path,default=None):
    try: return requests.get(API+path,timeout=3).json()
    except Exception: return default
try:
    health=get('/health',{}); st.caption(f"API status: {health.get('status','unavailable')} · Mode: {health.get('mode','offline')}")
except Exception: pass
page=st.sidebar.radio('Workspace',['Executive overview','Forecast & events','Production schedule','What-if simulation'])
if page=='Executive overview':
    k=get('/kpis',{}); cols=st.columns(4)
    for c,label,key in zip(cols,['Required units','Scheduled units','Unscheduled units','Machines used'],['required_units','scheduled_units','unscheduled_units','machines_used']): c.metric(label,k.get(key,'—'))
    st.subheader('Machine availability')
    st.dataframe(get('/machines',[]),use_container_width=True,hide_index=True)
    st.subheader('Current requirements')
    st.dataframe(get('/production-requirements',[]),use_container_width=True,hide_index=True)
elif page=='Forecast & events':
    st.subheader('7-day forecasts')
    st.dataframe(get('/forecast',[]),use_container_width=True,hide_index=True)
    st.subheader('Event intelligence')
    st.info('LLM is optional and not activated. The demo event form uses deterministic rules; no live key is loaded.')
    with st.form('event'):
        summary=st.text_input('Event summary','Manufacturing investment increases demand')
        direction=st.selectbox('Demand direction',['positive','negative','neutral'])
        severity=st.selectbox('Severity',['low','medium','high','critical'])
        relevance=st.slider('Relevance',0.,1.,.9); confidence=st.slider('Confidence',0.,1.,.85)
        if st.form_submit_button('Apply event'):
            response=requests.post(API+'/news-events',json={'summary':summary,'demand_direction':direction,'severity':severity,'relevance_score':relevance,'confidence':confidence},timeout=5)
            st.json(response.json())
    st.json(get('/news-impact',[]))
elif page=='Production schedule':
    jobs=get('/schedule',[]); st.dataframe(jobs,use_container_width=True,hide_index=True)
    if jobs:
        import pandas as pd
        df=pd.DataFrame(jobs); df['start_time']=pd.to_datetime(df['start_time']); df['end_time']=pd.to_datetime(df['end_time']); st.bar_chart(df,x='machine_id',y='duration_minutes',color='product_id')
    machines=get('/machines',[]); failed=st.selectbox('Inject machine failure',[m['machine_id'] for m in machines])
    if st.button('Simulate failure and reschedule'):
        st.json(requests.post(API+'/simulate/machine-failure',json={'machine_id':failed},timeout=10).json())
elif page=='What-if simulation':
    change=st.slider('Demand change (%)',-50,50,20); inv=st.number_input('Adjust P001 stock',-500,500,0); fail=st.selectbox('Machine failure',['None']+[m['machine_id'] for m in get('/machines',[])])
    if st.button('Generate new schedule'):
        payload={'demand_change_pct':change,'failed_machines':[] if fail=='None' else [fail],'inventory_adjustment':{'P001':inv}}
        st.json(requests.post(API+'/simulate/scenario',json=payload,timeout=10).json())
