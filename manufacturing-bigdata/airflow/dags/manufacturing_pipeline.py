"""Optional Airflow DAG; requires Airflow installed in the orchestration environment."""
from datetime import datetime
from airflow import DAG
from airflow.operators.bash import BashOperator
with DAG('manufacturing_daily_pipeline',start_date=datetime(2026,1,1),schedule='@daily',catchup=False,tags=['manufacturing','prototype']) as dag:
    generate=BashOperator(task_id='generate_synthetic_data',bash_command='python -m data_generator.generate --orders 2000 --sensor-events 10000')
    etl=BashOperator(task_id='spark_batch_etl',bash_command='python -m spark.batch_etl')
    generate >> etl
