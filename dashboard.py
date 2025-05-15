"""
InsuranceRAGBot Metrics Dashboard
Run with: streamlit run dashboard.py
"""
import streamlit as st
import pandas as pd
import altair as alt
import os
import json
from datetime import datetime, timedelta
import sys

# Add the project directory to the system path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import metrics tracker
from app.utils.metrics import MetricsTracker

# Set page configuration
st.set_page_config(
    page_title="InsuranceRAGBot Metrics Dashboard",
    page_icon="📊",
    layout="wide"
)

# Dashboard title
st.title("InsuranceRAGBot Metrics Dashboard")

# Sidebar filters
st.sidebar.header("Filters")

# Date range filter
st.sidebar.subheader("Date Range")
today = datetime.now().date()
days_ago = today - timedelta(days=7)

start_date = st.sidebar.date_input("Start Date", days_ago)
end_date = st.sidebar.date_input("End Date", today)

# Convert to datetime with time
start_datetime = datetime.combine(start_date, datetime.min.time())
end_datetime = datetime.combine(end_date, datetime.max.time())

# Agent type filter
st.sidebar.subheader("Agent Type")
agent_types = ["All", "developer", "writer", "tester", "sales", "router", "system"]
selected_agent = st.sidebar.selectbox("Select Agent", agent_types)

# Auto refresh
auto_refresh = st.sidebar.checkbox("Auto Refresh (15s)", value=False)
if auto_refresh:
    st.sidebar.write("Auto-refreshing enabled")
    refresh_interval = 15
else:
    refresh_interval = None

# Function to filter data by date range and agent type
def filter_data(df, start, end, agent=None):
    # Convert timestamp strings to datetime objects
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    # Filter by date range
    filtered = df[(df['timestamp'] >= start) & (df['timestamp'] <= end)]
    
    # Filter by agent type if specified
    if agent and agent != "All":
        filtered = filtered[filtered['agent_type'] == agent]
    
    return filtered

# Function to load metrics data
def load_metrics_data(metric_type):
    data = MetricsTracker.load_metrics(metric_type, limit=1000)
    
    if not data:
        st.warning(f"No {metric_type} data available yet")
        return pd.DataFrame()
    
    return pd.DataFrame(data)

# Main dashboard layout
st.subheader("System Overview")

# Create metrics containers
col1, col2, col3, col4 = st.columns(4)

# Load latency data
latency_df = load_metrics_data('latency')

if not latency_df.empty:
    # Filter data
    filtered_latency = filter_data(latency_df, start_datetime, end_datetime, selected_agent)
    
    # Calculate metrics
    avg_latency = filtered_latency['latency'].mean() if not filtered_latency.empty else 0
    total_queries = len(filtered_latency['query_id'].unique()) if not filtered_latency.empty else 0
    
    # Display metrics
    col1.metric("Average Response Time", f"{avg_latency:.2f}s")
    col2.metric("Total Queries", total_queries)

# Load token usage data
token_df = load_metrics_data('token_usage')

if not token_df.empty:
    # Filter data
    filtered_token = filter_data(token_df, start_datetime, end_datetime, selected_agent)
    
    # Calculate metrics
    total_tokens = filtered_token['total_tokens'].sum() if not filtered_token.empty else 0
    avg_tokens = filtered_token['total_tokens'].mean() if not filtered_token.empty else 0
    
    # Display metrics
    col3.metric("Total Tokens Used", f"{total_tokens:,}")
    col4.metric("Avg Tokens per Query", f"{avg_tokens:.1f}")

# Latency Over Time Chart
st.subheader("Response Latency Over Time")

if not latency_df.empty:
    filtered_latency = filter_data(latency_df, start_datetime, end_datetime, selected_agent)
    
    if not filtered_latency.empty:
        # Group by hour and operation
        filtered_latency['hour'] = filtered_latency['timestamp'].dt.floor('h')
        latency_by_hour = filtered_latency.groupby(['hour', 'operation'])['latency'].mean().reset_index()
        
        # Create line chart
        latency_chart = alt.Chart(latency_by_hour).mark_line().encode(
            x=alt.X('hour:T', title='Time'),
            y=alt.Y('latency:Q', title='Latency (seconds)'),
            color=alt.Color('operation:N', title='Operation'),
            tooltip=['hour:T', 'operation:N', 'latency:Q']
        ).properties(
            height=300
        ).interactive()
        
        st.altair_chart(latency_chart, use_container_width=True)
    else:
        st.info("No latency data available for the selected filters. Try expanding the date range or selecting 'All' agents.")
        st.markdown("""
        **To generate meaningful latency data:**
        1. Use the bot to answer several queries
        2. Each query generates latency metrics for different operations
        3. Allow time between queries to see time-based trends
        """)
else:
    st.info("No latency data available yet. Use the bot to answer some queries and metrics will be tracked automatically.")

# Agent Usage Analysis
st.subheader("Agent Usage Distribution")

col1, col2 = st.columns(2)

# Load agent usage data
agent_df = load_metrics_data('agent_usage')

if not agent_df.empty:
    filtered_agent = filter_data(agent_df, start_datetime, end_datetime)
    
    if not filtered_agent.empty:
        # Agent type distribution
        agent_counts = filtered_agent['agent_type'].value_counts().reset_index()
        agent_counts.columns = ['agent_type', 'count']
        
        agent_chart = alt.Chart(agent_counts).mark_bar().encode(
            x=alt.X('agent_type:N', title='Agent Type'),
            y=alt.Y('count:Q', title='Number of Queries'),
            color=alt.Color('agent_type:N', legend=None),
            tooltip=['agent_type:N', 'count:Q']
        ).properties(
            title='Queries by Agent Type',
            height=300
        )
        
        col1.altair_chart(agent_chart, use_container_width=True)
        
        # Query type distribution
        query_counts = filtered_agent['query_type'].value_counts().reset_index()
        query_counts.columns = ['query_type', 'count']
        
        query_chart = alt.Chart(query_counts).mark_bar().encode(
            x=alt.X('query_type:N', title='Query Type'),
            y=alt.Y('count:Q', title='Number of Queries'),
            color=alt.Color('query_type:N', legend=None),
            tooltip=['query_type:N', 'count:Q']
        ).properties(
            title='Queries by Query Type',
            height=300
        )
        
        col2.altair_chart(query_chart, use_container_width=True)
    else:
        col1.info("No agent usage data available for the selected filters")
        col2.info("No agent usage data available for the selected filters")
else:
    col1.info("No agent usage data available yet")
    col2.info("No agent usage data available yet")

# Token Usage Analysis
st.subheader("Token Usage Analysis")

if not token_df.empty:
    filtered_token = filter_data(token_df, start_datetime, end_datetime, selected_agent)
    
    if not filtered_token.empty:
        col1, col2 = st.columns(2)
        
        # Token usage by agent type
        token_by_agent = filtered_token.groupby('agent_type')['total_tokens'].sum().reset_index()
        
        token_agent_chart = alt.Chart(token_by_agent).mark_bar().encode(
            x=alt.X('agent_type:N', title='Agent Type'),
            y=alt.Y('total_tokens:Q', title='Total Tokens'),
            color=alt.Color('agent_type:N', legend=None),
            tooltip=['agent_type:N', 'total_tokens:Q']
        ).properties(
            title='Token Usage by Agent Type',
            height=300
        )
        
        col1.altair_chart(token_agent_chart, use_container_width=True)
        
        # Prompt vs Completion tokens
        token_ratio_df = filtered_token.copy()
        token_ratio_df = token_ratio_df.melt(
            id_vars=['agent_type', 'timestamp', 'query_id'],
            value_vars=['prompt_tokens', 'completion_tokens'],
            var_name='token_type', 
            value_name='tokens'
        )
        
        token_ratio_chart = alt.Chart(token_ratio_df).mark_bar().encode(
            x=alt.X('agent_type:N', title='Agent Type'),
            y=alt.Y('tokens:Q', title='Tokens'),
            color=alt.Color('token_type:N', title='Token Type'),
            tooltip=['agent_type:N', 'token_type:N', 'tokens:Q']
        ).properties(
            title='Prompt vs Completion Tokens by Agent Type',
            height=300
        )
        
        col2.altair_chart(token_ratio_chart, use_container_width=True)
        
        # Token usage over time
        filtered_token['hour'] = filtered_token['timestamp'].dt.floor('h')
        token_by_hour = filtered_token.groupby('hour')['total_tokens'].sum().reset_index()
        
        # Only create the time chart if we have enough data points
        if len(token_by_hour) > 1:
            token_time_chart = alt.Chart(token_by_hour).mark_line().encode(
                x=alt.X('hour:T', title='Time'),
                y=alt.Y('total_tokens:Q', title='Total Tokens'),
                tooltip=['hour:T', 'total_tokens:Q']
            ).properties(
                title='Token Usage Over Time',
                height=300
            ).interactive()
            
            st.altair_chart(token_time_chart, use_container_width=True)
        else:
            st.info("Not enough time data points to show token usage over time. More queries across different times are needed.")
    else:
        st.info("No token usage data available for the selected filters. Try expanding the date range or selecting 'All' agents.")
        st.markdown("""
        **To generate token usage data:**
        1. Use the bot to answer several queries
        2. Each query to an LLM-based agent generates token usage metrics
        3. The system tracks both prompt and completion tokens
        """)
else:
    st.info("No token usage data available yet. Use the bot to answer some queries and metrics will be tracked automatically.")

# Retrieval Metrics Analysis
st.subheader("Retrieval Metrics")

retrieval_df = load_metrics_data('retrieval')

if not retrieval_df.empty:
    filtered_retrieval = filter_data(retrieval_df, start_datetime, end_datetime)
    
    if not filtered_retrieval.empty and 'num_docs_retrieved' in filtered_retrieval.columns:
        avg_docs = filtered_retrieval['num_docs_retrieved'].mean()
        
        st.metric("Average Documents Retrieved", f"{avg_docs:.2f}")
        
        # Docs retrieved distribution
        docs_counts = filtered_retrieval['num_docs_retrieved'].value_counts().reset_index()
        docs_counts.columns = ['num_docs', 'count']
        
        docs_chart = alt.Chart(docs_counts).mark_bar().encode(
            x=alt.X('num_docs:Q', title='Number of Documents Retrieved'),
            y=alt.Y('count:Q', title='Frequency'),
            tooltip=['num_docs:Q', 'count:Q']
        ).properties(
            title='Distribution of Documents Retrieved per Query',
            height=300
        )
        
        st.altair_chart(docs_chart, use_container_width=True)
    else:
        st.info("No retrieval data available for the selected filters")
else:
    st.info("No retrieval data available yet")

# Set up auto-refresh if enabled
if auto_refresh:
    st.empty()
    st.rerun()

# Footer
st.sidebar.markdown("---")
st.sidebar.info(
    """
    **InsuranceRAGBot Metrics Dashboard**
    
    This dashboard shows real-time metrics for the InsuranceRAGBot multi-agent RAG system.
    """
) 