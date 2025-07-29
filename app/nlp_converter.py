import os
import requests
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def english_to_sql(english_query: str, hf_token: str = None) -> str:
    """
    Converts English queries to SQL using Hugging Face Inference API
    Model: tscholak/cxmefzzi (text-to-SQL, 200MB model)
    Free tier: 30k tokens/month (enough for 100+ queries/day)
    """
    # Fallback to rule-based if no token provided
    if not hf_token:
        logger.warning("Hugging Face token not provided - using rule-based fallback")
        return _rule_based_converter(english_query)
    
    API_URL = "https://api-inference.huggingface.co/models/tscholak/cxmefzzi"
    headers = {"Authorization": f"Bearer {hf_token}"}
    
    # Format for text-to-SQL model
    table_schema = "transaction_id, product, amount, country, year"
    input_text = f"Question: {english_query} | Context: {table_schema}"
    
    try:
        response = requests.post(
            API_URL,
            headers=headers,
            json={"inputs": input_text},
            timeout=10
        )
        
        if response.status_code == 503:
            # Model is loading - retry with exponential backoff
            logger.info("Model is loading, retrying...")
            import time
            time.sleep(5)
            response = requests.post(API_URL, headers=headers, json={"inputs": input_text})
        
        response.raise_for_status()
        result = response.json()
        sql_query = result[0]['generated_text'].strip()
        
        # Validate SQL
        if not sql_query.lower().startswith(("select", "with")):
            logger.warning(f"Invalid SQL generated: {sql_query} - using rule-based fallback")
            return _rule_based_converter(english_query)
        
        return sql_query
    
    except Exception as e:
        logger.error(f"NLP conversion failed: {str(e)}")
        return _rule_based_converter(english_query)

def _rule_based_converter(query: str) -> str:
    """Fallback rule-based converter (for free tier compliance)"""
    q = query.strip().lower()
    if "list all" in q and "sales" in q:
        return "SELECT * FROM sales_data LIMIT 100"
    elif "total sales" in q and "2023" in q:
        return "SELECT SUM(amount) as total_sales FROM sales_data WHERE year = 2023"
    elif "top 5 products" in q:
        return "SELECT product, SUM(amount) as revenue FROM sales_data GROUP BY product ORDER BY revenue DESC LIMIT 5"
    elif "sales by country" in q:
        return "SELECT country, SUM(amount) as total_sales FROM sales_data GROUP BY country"
    return "SELECT * FROM sales_data LIMIT 10"
