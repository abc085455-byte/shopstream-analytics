from datetime import datetime, timedelta
from airflow import DAG
from airflow.providers.standard.operators.python import PythonOperator
from airflow.providers.standard.operators.empty import EmptyOperator
from airflow.task.trigger_rule import TriggerRule
from airflow.models import Variable
import logging

logger = logging.getLogger(__name__)

default_args = {
    'owner': 'shopstream-de-team',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=3),
}

with DAG(
    dag_id='shopstream_master_pipeline',
    default_args=default_args,
    description='ShopStream Analytics — S3 to Snowflake',
    schedule='0 2 * * *',
    catchup=False,
    max_active_runs=1,
    tags=['shopstream', 'production'],
) as dag:

    pipeline_start = EmptyOperator(task_id='pipeline_start')

    def ingest_table(table_name, s3_prefix, columns, **context):
        import boto3, snowflake.connector, pandas as pd, io, os
        run_date  = context['ds']
        date_path = run_date.replace('-', '/')
        bucket    = Variable.get('aws_s3_bucket', default_var='shopstream-raw-data')
        batch_id  = f"{table_name}_{run_date}"

        s3 = boto3.client(
            's3',
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
            region_name=os.getenv('AWS_DEFAULT_REGION', 'us-east-1'),
        )
        s3_key = f"ecommerce/{s3_prefix}/{date_path}/{s3_prefix}.csv"
        try:
            obj = s3.get_object(Bucket=bucket, Key=s3_key)
            df  = pd.read_csv(io.BytesIO(obj['Body'].read()))
            logger.info(f"[{table_name}] Read {len(df)} rows")
        except Exception as e:
            logger.warning(f"[{table_name}] File not found: {e}")
            return 0

        df['_source_file']      = f"s3://{bucket}/{s3_key}"
        df['_source_loaded_at'] = datetime.utcnow().isoformat()
        df['_batch_id']         = batch_id
        df = df.astype(str).replace('nan', None)

        conn = snowflake.connector.connect(
            account='FIARMWM-NQ08270',
            user=Variable.get('snowflake_user', default_var='MUHAMMADSHAWAIL'),
            password=Variable.get('snowflake_password', default_var=''),
            database='SHOPSTREAM_DB',
            warehouse='SHOPSTREAM_WH',
            role='ACCOUNTADMIN',
            schema='RAW',
        )
        cursor = conn.cursor()
        cursor.execute(f"DELETE FROM RAW.{table_name} WHERE _batch_id = '{batch_id}'")
        all_cols     = columns + ['_source_file', '_source_loaded_at', '_batch_id']
        col_names    = ', '.join(all_cols)
        placeholders = ', '.join(['%s'] * len(all_cols))
        data = [tuple(row) for row in df[all_cols].values]
        cursor.executemany(
            f"INSERT INTO RAW.{table_name} ({col_names}) VALUES ({placeholders})",
            data
        )
        conn.commit()
        conn.close()
        logger.info(f"[{table_name}] ✅ {len(df)} rows loaded")
        return len(df)

    task_ingest_orders = PythonOperator(
        task_id='ingest_orders_from_s3',
        python_callable=ingest_table,
        op_kwargs={
            'table_name': 'ORDERS',
            's3_prefix': 'orders',
            'columns': [
                'order_id','customer_id','order_date','order_status',
                'payment_method','payment_status','shipping_address',
                'total_amount','discount_amount','tax_amount',
                'currency','created_at','updated_at'
            ],
        },
    )

    task_ingest_customers = PythonOperator(
        task_id='ingest_customers_from_s3',
        python_callable=ingest_table,
        op_kwargs={
            'table_name': 'CUSTOMERS',
            's3_prefix': 'customers',
            'columns': [
                'customer_id','first_name','last_name','email','phone',
                'date_of_birth','gender','country','city',
                'signup_date','customer_segment','is_active'
            ],
        },
    )

    task_ingest_products = PythonOperator(
        task_id='ingest_products_from_s3',
        python_callable=ingest_table,
        op_kwargs={
            'table_name': 'PRODUCTS',
            's3_prefix': 'products',
            'columns': [
                'product_id','product_name','category','sub_category',
                'brand','sku','cost_price','selling_price',
                'stock_quantity','is_active','created_date'
            ],
        },
    )

    task_ingest_events = PythonOperator(
        task_id='ingest_events_from_s3',
        python_callable=ingest_table,
        op_kwargs={
            'table_name': 'EVENTS',
            's3_prefix': 'events',
            'columns': [
                'event_id','session_id','customer_id','event_type',
                'event_timestamp','page_url','product_id',
                'device_type','browser','ip_address','properties'
            ],
        },
    )

    ingestion_done = EmptyOperator(
        task_id='ingestion_complete',
        trigger_rule=TriggerRule.ALL_SUCCESS,
    )

    pipeline_end = EmptyOperator(
        task_id='pipeline_complete',
        trigger_rule=TriggerRule.ALL_SUCCESS,
    )

    pipeline_start >> [
        task_ingest_orders,
        task_ingest_customers,
        task_ingest_products,
        task_ingest_events,
    ] >> ingestion_done >> pipeline_end