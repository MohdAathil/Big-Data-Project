"""Optional PySpark CSV-to-Parquet batch ETL."""
import argparse
from pyspark.sql import SparkSession
from pyspark.sql.functions import to_date, col, year, month

def main():
    p=argparse.ArgumentParser(); p.add_argument('--input',default='data/raw'); p.add_argument('--output',default='data/processed'); a=p.parse_args()
    spark=SparkSession.builder.appName('manufacturing-batch-etl').getOrCreate()
    orders=spark.read.option('header',True).option('inferSchema',True).csv(f'{a.input}/customer_orders.csv')
    orders=orders.withColumn('order_date',to_date(col('order_date'))).withColumn('year',year('order_date')).withColumn('month',month('order_date')).repartition('year','month')
    orders.write.mode('overwrite').partitionBy('year','month').parquet(f'{a.output}/orders')
    spark.stop()
if __name__=='__main__': main()
