"""Failure-event demo hook. Posts a simulated machine failure to the API."""
import argparse, os, requests
p=argparse.ArgumentParser(); p.add_argument('machine_id'); p.add_argument('--api',default=os.getenv('API_BASE_URL','http://localhost:8000')); a=p.parse_args()
r=requests.post(a.api+'/simulate/machine-failure',json={'machine_id':a.machine_id},timeout=15); r.raise_for_status(); print(r.json())
