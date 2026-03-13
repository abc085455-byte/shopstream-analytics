"""
ShopStream Analytics — S3 Data Extractor
=========================================
Pulls files from AWS S3 and loads them into Snowflake RAW schema.
Supports CSV and JSON formats.
"""

import boto3
import snowflake.connector
import pandas as pd
import logging
import os
import io
from datetime import datetime
from typing import Optional

logger = logging.getLogger(__name__)


class S3Extractor:
    """
    Extract data from S3 and load into Snowflake RAW tables.

    Usage:
        extractor = S3Extractor(
            bucket='shopstream-raw-data',
            prefix='ecommerce/orders/2024/01/15/'
        )
        records_loaded = extractor.extract_and_load(
            target_table='RAW.ORDERS',
            batch_id='orders_2024-01-15_run123'
        )
    """

    def __init__(self, bucket: str, prefix: str):
        self.bucket = bucket
        self.prefix = prefix
        self.s3_client = self._init_s3()
        self.snowflake_conn = self._init_snowflake()

    def _init_s3(self):
        """Initialize S3 client using env vars or IAM role"""
        return boto3.client(
            's3',
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
            region_name=os.getenv('AWS_DEFAULT_REGION', 'us-east-1')
        )

    def _init_snowflake(self):
        """Initialize Snowflake connection"""
        return snowflake.connector.connect(
            account=os.getenv('SNOWFLAKE_ACCOUNT'),
            user=os.getenv('SNOWFLAKE_USER'),
            password=os.getenv('SNOWFLAKE_PASSWORD'),
            database=os.getenv('SNOWFLAKE_DATABASE', 'SHOPSTREAM_DB'),
            warehouse=os.getenv('SNOWFLAKE_WAREHOUSE', 'SHOPSTREAM_WH'),
            role=os.getenv('SNOWFLAKE_ROLE', 'SHOPSTREAM_LOADER'),
            schema='RAW'
        )

    def list_files(self) -> list:
        """List all files in S3 prefix"""
        response = self.s3_client.list_objects_v2(
            Bucket=self.bucket,
            Prefix=self.prefix
        )

        if 'Contents' not in response:
            logger.warning(f"No files found at s3://{self.bucket}/{self.prefix}")
            return []

        files = [obj['Key'] for obj in response['Contents']
                 if not obj['Key'].endswith('/')]
        logger.info(f"Found {len(files)} files at s3://{self.bucket}/{self.prefix}")
        return files

    def read_file(self, s3_key: str) -> pd.DataFrame:
        """Read a single file from S3 into DataFrame"""
        logger.info(f"Reading s3://{self.bucket}/{s3_key}")

        obj = self.s3_client.get_object(Bucket=self.bucket, Key=s3_key)
        content = obj['Body'].read()

        if s3_key.endswith('.csv'):
            df = pd.read_csv(io.BytesIO(content))
        elif s3_key.endswith('.json') or s3_key.endswith('.jsonl'):
            df = pd.read_json(io.BytesIO(content), lines=s3_key.endswith('.jsonl'))
        elif s3_key.endswith('.parquet'):
            df = pd.read_parquet(io.BytesIO(content))
        else:
            raise ValueError(f"Unsupported file format: {s3_key}")

        logger.info(f"Read {len(df)} rows from {s3_key}")
        return df

    def add_metadata(self, df: pd.DataFrame, s3_key: str, batch_id: str) -> pd.DataFrame:
        """Add pipeline metadata columns"""
        df['_source_file'] = f"s3://{self.bucket}/{s3_key}"
        df['_source_loaded_at'] = datetime.utcnow().isoformat()
        df['_batch_id'] = batch_id
        # Convert all columns to string for raw layer (typed in staging)
        return df.astype(str)

    def load_to_snowflake(self, df: pd.DataFrame, target_table: str) -> int:
        """Load DataFrame into Snowflake table using bulk insert"""
        cursor = self.snowflake_conn.cursor()

        # Convert DataFrame to list of tuples
        columns = list(df.columns)
        values = [tuple(row) for row in df.values]

        placeholders = ', '.join(['%s'] * len(columns))
        col_names = ', '.join(columns)
        sql = f"INSERT INTO {target_table} ({col_names}) VALUES ({placeholders})"

        cursor.executemany(sql, values)
        self.snowflake_conn.commit()

        rows_inserted = len(values)
        logger.info(f"Loaded {rows_inserted} rows into {target_table}")
        cursor.close()
        return rows_inserted

    def extract_and_load(self, target_table: str, batch_id: str) -> int:
        """
        Main method: list S3 files → read → add metadata → load to Snowflake
        Returns total records loaded
        """
        files = self.list_files()
        if not files:
            logger.warning(f"No files to process for batch: {batch_id}")
            return 0

        total_records = 0
        failed_files = []

        for s3_key in files:
            try:
                df = self.read_file(s3_key)
                df = self.add_metadata(df, s3_key, batch_id)
                records = self.load_to_snowflake(df, target_table)
                total_records += records

            except Exception as e:
                logger.error(f"Failed to process {s3_key}: {str(e)}")
                failed_files.append(s3_key)

        if failed_files:
            logger.error(f"Failed files: {failed_files}")
            raise RuntimeError(
                f"Ingestion partially failed. "
                f"{len(failed_files)}/{len(files)} files failed. "
                f"Check logs for details."
            )

        logger.info(
            f"Batch {batch_id} complete: "
            f"{total_records} total records loaded into {target_table}"
        )
        self.snowflake_conn.close()
        return total_records
