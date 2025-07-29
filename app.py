import streamlit as st
from app.nlp_converter import english_to_sql
from app.athena_executor import run_athena_query
import pandas as pd
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    st.set_page_config(
        page_title="NLP to SQL Converter",
        page_icon="🔍",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.title("🔍 Natural Language to SQL Converter")
    st.markdown("""
    **Convert English questions to SQL queries** and get instant results from Amazon Athena.
    
    *All infrastructure runs on AWS free tier - no cost to you!*
    """)
    
    # Input form
    with st.form("query_form"):
        user_query = st.text_area(
            "Ask a question about your data",
            height=100,
            placeholder="Try: 'Which country had the highest sales in 2023?' or 'Show top 5 products by revenue'",
            help="Type your question in plain English and we'll convert it to SQL"
        )
        submitted = st.form_submit_button("Convert & Execute", type="primary")
    
    if submitted and user_query.strip() != "":
        try:
            # Convert English to SQL
            with st.spinner("🧠 Converting your question to SQL..."):
                logger.info(f"Converting query: {user_query}")
                sql_query = english_to_sql(user_query)
            
            # Show generated SQL
            st.subheader("🔧 Generated SQL Query")
            st.code(sql_query, language='sql')
            
            # Execute on Athena
            st.subheader("📊 Query Results")
            with st.spinner("⏳ Running query on Athena..."):
                # Get config from Streamlit secrets
                try:
                    aws_region = st.secrets["aws"]["region"]
                    athena_database = st.secrets["athena"]["database"]
                    s3_output = st.secrets["athena"]["output_location"]
                    hf_token = st.secrets.get("huggingface", {}).get("token", None)
                except Exception as e:
                    st.error("⚠️ Configuration error: Missing secrets.toml file")
                    st.info("""
                    **To fix this:**
                    1. Create a secrets.toml file in your .streamlit folder
                    2. Add your AWS and Hugging Face credentials
                    3. Restart the app
                    """)
                    logger.exception("Secrets configuration error")
                    st.stop()
                
                # Execute query
                df = run_athena_query(
                    sql_query,
                    athena_database,
                    s3_output,
                    region_name=aws_region
                )
            
            # Display results
            if not df.empty:
                st.success("✅ Query executed successfully!")
                
                # Show data table
                st.dataframe(df)
                
                # Auto-detect visualization type based on columns
                if len(df.columns) == 2:
                    col1, col2 = df.columns
                    if df[col2].dtype in ['int64', 'float64']:
                        st.subheader("📈 Visualization")
                        st.bar_chart(df.set_index(col1)[col2])
                    else:
                        st.info("📊 Data is displayed as a table (no numeric values to chart)")
                
                # CSV download
                st.download_button(
                    label="📥 Download as CSV",
                    data=df.to_csv(index=False),
                    file_name="query_results.csv",
                    mime="text/csv"
                )
            else:
                st.warning("⚠️ Query executed successfully but returned no results.")
                st.info("Try modifying your question or check the data available in the database.")
                
        except Exception as e:
            st.error(f"❌ Execution failed: {str(e)}")
            logger.exception("Query execution error")
            st.exception(e)
    
    # Example queries for users
    with st.sidebar:
        st.header("💡 Example Queries")
        st.markdown("""
        - Total sales in 2023
        - Top 5 products by revenue
        - Sales breakdown by country
        - List all sales records
        - Which country had the highest sales?
        - Average product price by category
        """)
        
        st.divider()
        
        st.subheader("⚙️ System Status")
        st.success("Athena: Connected")
        st.success("S3: Connected")
        st.info("Hugging Face: Using free tier (30k tokens/month)")
        
        st.divider()
        
        st.caption("""
        **AWS Free Tier Compliant**  
        - Athena: First 1 TB free/month
        - S3: 5 GB free storage
        - Hugging Face: 30k tokens free/month
        """)

if __name__ == "__main__":
    main()
