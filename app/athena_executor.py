import boto3
import time
import pandas as pd
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_athena_query(sql: str, database: str, output_location: str, region_name='us-east-1') -> pd.DataFrame:
    """
    Executes SQL on Athena and returns results as DataFrame
    
    Args:
        sql: SQL query to execute
        database: Athena database name
        output_location: S3 path for query results (e.g., 's3://bucket-name/')
        region_name: AWS region
        
    Returns:
        pandas DataFrame with query results
    """
    logger.info(f"Starting Athena query execution in {region_name}")
    logger.debug(f"Query: {sql}")
    
    client = boto3.client('athena', region_name=region_name)
    
    try:
        # Start query execution
        response = client.start_query_execution(
            QueryString=sql,
            QueryExecutionContext={'Database': database},
            ResultConfiguration={'OutputLocation': output_location}
        )
        query_execution_id = response['QueryExecutionId']
        logger.info(f"Query execution ID: {query_execution_id}")
        
        # Poll until query completes
        while True:
            result = client.get_query_execution(QueryExecutionId=query_execution_id)
            state = result['QueryExecution']['Status']['State']
            logger.debug(f"Query state: {state}")
            
            if state in ['SUCCEEDED', 'FAILED', 'CANCELLED']:
                break
                
            time.sleep(1)
        
        if state != 'SUCCEEDED':
            reason = result['QueryExecution']['Status'].get('StateChangeReason', 'Unknown error')
            logger.error(f"Query failed: {reason}")
            raise Exception(f"Query failed: {reason}")
        
        # Fetch results
        results = client.get_query_results(QueryExecutionId=query_execution_id)
        rows = results['ResultSet']['Rows']
        
        # Convert to DataFrame
        headers = [col['Name'] for col in results['ResultSet']['ResultSetMetadata']['ColumnInfo']]
        data = []
        for row in rows[1:]:  # Skip header
            values = [data_field.get('VarCharValue', '') for data_field in row['Data']]
            data.append(values)
        
        logger.info(f"Query succeeded with {len(data)} rows returned")
        return pd.DataFrame(data, columns=headers)
        
    except Exception as e:
        logger.exception("Athena query execution failed")
        raise
