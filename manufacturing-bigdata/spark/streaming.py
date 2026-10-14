"""Consume machine/order events from Kafka with Spark Structured Streaming.

Example: python -m spark.streaming --brokers localhost:9092 --topic machine_events
"""
import argparse
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json, to_timestamp
from pyspark.sql.types import StructType, StructField, StringType, DoubleType

SCHEMA=StructType([StructField('event_id',StringType()),StructField('machine_id',StringType()),StructField('timestamp',StringType()),StructField('event_type',StringType()),StructField('status',StringType()),StructField('temperature',DoubleType()),StructField('vibration',DoubleType())])
def main():
    p=argparse.ArgumentParser(); p.add_argument('--brokers',default='localhost:9092'); p.add_argument('--topic',default='machine_events'); p.add_argument('--checkpoint',default='data/checkpoints/spark_streaming'); a=p.parse_args()
    spark=SparkSession.builder.appName('manufacturing-kafka-stream').getOrCreate()
    raw=spark.readStream.format('kafka').option('kafka.bootstrap.servers',a.brokers).option('subscribe',a.topic).option('startingOffsets','latest').load()
    parsed=raw.select(from_json(col('value').cast('string'),SCHEMA).alias('event')).select('event.*').withColumn('event_time',to_timestamp('timestamp')).withWatermark('event_time','10 minutes')
    query=parsed.writeStream.format('console').outputMode('append').option('truncate','false').option('checkpointLocation',a.checkpoint).start()
    query.awaitTermination()
if __name__=='__main__': main()
