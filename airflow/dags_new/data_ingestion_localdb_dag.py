import os
from datetime import datetime

from airflow import DAG

from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator

from ingest_script import ingest_callable

AIRFLOW_HOME = os.environ.get("AIRFLOW_HOME", "/opt/airflow/")

PG_USER = os.getenv ('PG_USER')
PG_PASSWORD = os.getenv ('PG_PASSWORD')
PG_HOST = os.getenv ('PG_HOST')
PG_PORT = os.getenv ('PG_PORT')
PG_DATABASE = os.getenv ('PG_DATABASE')

local_workflow = DAG(
    #Name the dag
    "local_ingestion_dag",
    #cron expressions can be added as well
    schedule_interval= "@monthly",
    start_date = datetime(2023,1,1)
)

url = f"https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_" + "{{execution_date.strftime(\'%Y-%m\')}}.parquet"
OUTPUT_FILE_TEMPLATE = AIRFLOW_HOME + '/output_{{ execution_date.strftime(\'%Y-%m\') }}.parquet'
TABLE_NAME = "yellow_taxi_{{ execution_date.strftime(\'%Y_%m\') }}"

with local_workflow:

    wget_task = BashOperator(
        task_id = "wget",
        bash_command = f'curl -sSL {url} > {OUTPUT_FILE_TEMPLATE}'
        #bash_command='echo "{{execution_date.strftime(\'%Y-%m\')}}"'
    )

    ingest_task = PythonOperator(
        task_id="ingest",
        python_callable= ingest_callable,
        op_kwargs= dict(
            user = PG_USER,
            password = PG_PASSWORD,
            host = PG_HOST,
            port = PG_PORT,
            db = PG_DATABASE,
            table_name = TABLE_NAME,
            parquet_file = OUTPUT_FILE_TEMPLATE,
            execution_date = "{{ execution_date.strftime(\'%Y-%m\') }}"
        )
    )

    wget_task >> ingest_task    