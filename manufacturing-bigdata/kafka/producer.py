"""Publish one JSON event to Kafka; requires kafka-python and a running broker."""
import argparse, json, os
from datetime import datetime, timezone
from kafka import KafkaProducer

def main():
    p=argparse.ArgumentParser(); p.add_argument('--topic',default='machine_events'); p.add_argument('--machine',default='M002'); p.add_argument('--event',default='FAILURE'); p.add_argument('--brokers',default=os.getenv('KAFKA_BOOTSTRAP_SERVERS','localhost:9092')); a=p.parse_args()
    producer=KafkaProducer(bootstrap_servers=a.brokers.split(','),value_serializer=lambda x:json.dumps(x).encode('utf-8'))
    event={'event_id':f'{a.machine}-{datetime.now(timezone.utc).timestamp()}','machine_id':a.machine,'timestamp':datetime.now(timezone.utc).isoformat(),'event_type':a.event,'status':'FAILED' if a.event.upper()=='FAILURE' else 'RUNNING'}
    producer.send(a.topic,event).get(timeout=15); producer.flush(); producer.close(); print(json.dumps(event))
if __name__=='__main__': main()
