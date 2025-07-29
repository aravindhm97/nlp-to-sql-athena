import boto3
import argparse
import time

def create_athena_table(region, bucket, database):
    athena = boto3.client('athena', region_name=region)
    
    # Create database if not exists
    athena.start_query_execution(
        QueryString=f"CREATE DATABASE IF NOT EXISTS {database}",
        ResultConfiguration={'OutputLocation': f's3://{bucket}-results/'}
    )
    
    # Wait for database creation
    time.sleep(2)
    
    # Create table
    create_table_query = f"""
    CREATE EXTERNAL TABLE IF NOT EXISTS {database}.sales_data (
        transaction_id INT,
        product STRING,
        amount INT,
        country STRING,
        year INT
    )
    ROW FORMAT DELIMITED
    FIELDS TERMINATED BY ','
    STORED AS TEXTFILE
    LOCATION 's3://{bucket}/'
    TBLPROPERTIES ('skip.header.line.count'='1')
    """
    
    response = athena.start_query_execution(
        QueryString=create_table_query,
        QueryExecutionContext={'Database': database},
        ResultConfiguration={'OutputLocation': f's3://{bucket}-results/'}
    )
    
    # Wait for table creation
    while True:
        result = athena.get_query_execution(QueryExecutionId=response['QueryExecutionId'])
        state = result['QueryExecution']['Status']['State']
        if state in ['SUCCEEDED', 'FAILED', 'CANCELLED']:
            break
        time.sleep(1)
    
    if state != 'SUCCEEDED':
        raise Exception(f"Table creation failed: {result['QueryExecution']['Status']['StateChangeReason']}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--region', required=True)
    parser.add_argument('--bucket', required=True)
    parser.add_argument('--database', required=True)
    args = parser.parse_args()
    
    create_athena_table(args.region, args.bucket, args.database)
