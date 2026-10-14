"""Fetch and deduplicate recent GDELT article metadata for configured keywords."""
import argparse, json, time
from pathlib import Path
import requests

GDELT_URL='https://api.gdeltproject.org/api/v2/doc/doc'

def fetch_articles(query, limit=50):
    r=requests.get(GDELT_URL,params={'query':query,'mode':'ArtList','format':'json','maxrecords':min(250,limit),'sort':'DateDesc'},timeout=30)
    r.raise_for_status()
    payload=r.json()
    return payload.get('articles',[])

def main():
    p=argparse.ArgumentParser(); p.add_argument('--query',default='manufacturing OR semiconductor shortage OR logistics disruption'); p.add_argument('--output',default='data/raw/news.jsonl'); p.add_argument('--limit',type=int,default=50); a=p.parse_args()
    articles=fetch_articles(a.query,a.limit); seen=set(); out=[]
    for item in articles:
        url=item.get('url')
        if not url or url in seen: continue
        seen.add(url); out.append({'title':item.get('title',''),'url':url,'source':item.get('domain',''),'publication_time':item.get('seendate'),'ingestion_time':int(time.time()),'query':a.query})
    dest=Path(a.output); dest.parent.mkdir(parents=True,exist_ok=True); dest.write_text(''.join(json.dumps(x)+'\n' for x in out),encoding='utf-8')
    print(f'Saved {len(out)} deduplicated articles to {dest}')
if __name__=='__main__': main()
