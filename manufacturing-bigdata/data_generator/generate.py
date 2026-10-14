"""Streaming synthetic CSV generation: all generated records are simulated."""
import argparse, csv, random
from datetime import datetime, timedelta
from pathlib import Path

PRODUCTS = [
    ('P001','Drive Module','ELECTRONICS',42,18,'copper',2.0),
    ('P002','Control Unit','ELECTRONICS',35,15,'circuit_board',1.0),
    ('P003','Pump Assembly','MECHANICAL',55,22,'steel',4.5),
    ('P004','Sensor Pack','ELECTRONICS',24,12,'silicon',0.4),
    ('P005','Valve Kit','MECHANICAL',30,16,'aluminum',1.8),
]
MACHINES = [
    ('M001','CNC',70,.92,48,'P001|P003|P005'),
    ('M002','ASSEMBLY',90,.88,35,'P001|P002|P004'),
    ('M003','ELECTRONICS',110,.95,42,'P002|P004|P005'),
    ('M004','MIXED',55,.84,30,'P001|P003|P004'),
]

def write_csv(path, header, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w', newline='', encoding='utf-8') as f:
        w=csv.writer(f); w.writerow(header); w.writerows(rows)

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--orders',type=int,default=2000); ap.add_argument('--sensor-events',type=int,default=10000); ap.add_argument('--scale',choices=['small','medium','large'])
    a=ap.parse_args();
    if a.scale: a.orders,a.sensor_events={'small':(100_000,250_000),'medium':(1_000_000,2_000_000),'large':(5_000_000,10_000_000)}[a.scale]
    random.seed(17); out=Path('data/raw'); now=datetime.now().replace(hour=8,minute=0,second=0,microsecond=0)
    write_csv(out/'products.csv',['product_id','product_name','category','processing_time_minutes','setup_time_minutes','required_material','material_per_unit'],PRODUCTS)
    write_csv(out/'machines.csv',['machine_id','machine_type','capacity_units_per_hour','efficiency','operating_cost_per_hour','supported_products'],MACHINES)
    write_csv(out/'inventory.csv',['product_id','warehouse_id','current_stock','safety_stock','reorder_level','incoming_quantity','reserved_quantity'],((p[0],'WH1',random.randint(80,800),100,120,random.randint(0,200),random.randint(0,50)) for p in PRODUCTS))
    write_csv(out/'customer_orders.csv',['order_id','customer_id','product_id','order_date','quantity','priority','promised_date','status'],((f'O{i:08}',f'C{random.randint(1,200):04}',random.choice(PRODUCTS)[0],(now-timedelta(days=random.randint(0,90))).date(),random.randint(10,400),random.choice(['LOW','NORMAL','HIGH','URGENT']),(now+timedelta(days=random.randint(1,20))).date(),'OPEN') for i in range(a.orders)))
    def production_rows():
        for i in range(max(1000,a.orders//3)):
            start=now-timedelta(days=random.randint(1,120)); q=random.randint(20,200); defects=random.randint(0,3)
            yield (f'PR{i:08}',random.choice(MACHINES)[0],random.choice(PRODUCTS)[0],start,start+timedelta(hours=2),q,q-defects,defects,random.randint(10,30),random.randint(0,25))
    write_csv(out/'production_history.csv',['production_id','machine_id','product_id','start_time','end_time','quantity_planned','quantity_completed','defect_quantity','setup_minutes','downtime_minutes'],production_rows())
    write_csv(out/'maintenance.csv',['maintenance_id','machine_id','maintenance_type','start_time','end_time','reason','severity'],((f'MNT{i:04}',m[0],'PREVENTIVE',now+timedelta(days=i%30,hours=12),now+timedelta(days=i%30,hours=14),'Scheduled service','MEDIUM') for i,m in enumerate(MACHINES)))
    def events():
        for i in range(a.sensor_events):
            m=random.choice(MACHINES)[0]; yield (f'E{i:09}',m,now+timedelta(seconds=i*4),'HEALTH',round(random.gauss(70,8),2),round(max(0,random.gauss(2.2,.7)),3),round(random.gauss(5,1),2),'RUNNING')
    write_csv(out/'machine_events.csv',['event_id','machine_id','timestamp','event_type','temperature','vibration','pressure','status'],events())
    print(f'Generated simulated data in {out}: {a.orders:,} orders, {a.sensor_events:,} sensor events')
if __name__=='__main__': main()
