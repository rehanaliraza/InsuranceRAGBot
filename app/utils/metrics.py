"""
Metrics tracking module for the InsuranceRAGBot application
"""
import time
import json
import os
from datetime import datetime
from typing import Dict, Any, List, Optional
import logging

# Configure logging
logger = logging.getLogger("metrics")
logger.setLevel(logging.INFO)

# Create metrics directory if it doesn't exist
METRICS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "metrics")
os.makedirs(METRICS_DIR, exist_ok=True)

# File paths
LATENCY_FILE = os.path.join(METRICS_DIR, "latency.jsonl")
TOKEN_USAGE_FILE = os.path.join(METRICS_DIR, "token_usage.jsonl")
RETRIEVAL_METRICS_FILE = os.path.join(METRICS_DIR, "retrieval.jsonl")
AGENT_USAGE_FILE = os.path.join(METRICS_DIR, "agent_usage.jsonl")

class MetricsTracker:
    """Tracks various metrics for the InsuranceRAGBot"""
    
    @staticmethod
    def track_latency(operation: str, agent_type: str, latency: float, query_id: Optional[str] = None):
        """
        Track latency for various operations
        
        Args:
            operation: Type of operation (e.g., 'retrieval', 'agent_response', 'total')
            agent_type: Type of agent used
            latency: Time taken in seconds
            query_id: Unique identifier for the query
        """
        data = {
            "timestamp": datetime.now().isoformat(),
            "operation": operation,
            "agent_type": agent_type,
            "latency": latency,
            "query_id": query_id or f"query_{int(time.time())}"
        }
        
        with open(LATENCY_FILE, 'a') as f:
            f.write(json.dumps(data) + '\n')
        
        logger.info(f"Tracked latency: {latency:.2f}s for {operation} ({agent_type})")
    
    @staticmethod
    def track_token_usage(agent_type: str, prompt_tokens: int, completion_tokens: int, 
                         model: str, query_id: Optional[str] = None):
        """
        Track token usage for LLM calls
        
        Args:
            agent_type: Type of agent used
            prompt_tokens: Number of tokens in the prompt
            completion_tokens: Number of tokens in the completion
            model: Model name
            query_id: Unique identifier for the query
        """
        data = {
            "timestamp": datetime.now().isoformat(),
            "agent_type": agent_type,
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": prompt_tokens + completion_tokens,
            "model": model,
            "query_id": query_id or f"query_{int(time.time())}"
        }
        
        with open(TOKEN_USAGE_FILE, 'a') as f:
            f.write(json.dumps(data) + '\n')
        
        logger.info(f"Tracked token usage: {prompt_tokens + completion_tokens} tokens for {agent_type}")
    
    @staticmethod
    def track_retrieval_metrics(query: str, num_docs_retrieved: int, 
                               relevance_score: Optional[float] = None,
                               query_id: Optional[str] = None):
        """
        Track metrics related to document retrieval
        
        Args:
            query: User query
            num_docs_retrieved: Number of documents retrieved
            relevance_score: Optional score indicating relevance of retrieved documents
            query_id: Unique identifier for the query
        """
        data = {
            "timestamp": datetime.now().isoformat(),
            "query": query,
            "num_docs_retrieved": num_docs_retrieved,
            "query_id": query_id or f"query_{int(time.time())}"
        }
        
        if relevance_score is not None:
            data["relevance_score"] = relevance_score
        
        with open(RETRIEVAL_METRICS_FILE, 'a') as f:
            f.write(json.dumps(data) + '\n')
        
        logger.info(f"Tracked retrieval: {num_docs_retrieved} docs for query")
    
    @staticmethod
    def track_agent_usage(agent_type: str, query_type: str, query_id: Optional[str] = None):
        """
        Track which agent types are being used
        
        Args:
            agent_type: Type of agent used
            query_type: Type of query (e.g., 'general', 'technical', 'sales')
            query_id: Unique identifier for the query
        """
        data = {
            "timestamp": datetime.now().isoformat(),
            "agent_type": agent_type,
            "query_type": query_type,
            "query_id": query_id or f"query_{int(time.time())}"
        }
        
        with open(AGENT_USAGE_FILE, 'a') as f:
            f.write(json.dumps(data) + '\n')
        
        logger.info(f"Tracked agent usage: {agent_type} for {query_type} query")

    @staticmethod
    def load_metrics(metric_type: str, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Load metrics data for a specific metric type
        
        Args:
            metric_type: Type of metric ('latency', 'token_usage', 'retrieval', 'agent_usage')
            limit: Maximum number of records to load
        
        Returns:
            List of metric records
        """
        file_mapping = {
            'latency': LATENCY_FILE,
            'token_usage': TOKEN_USAGE_FILE,
            'retrieval': RETRIEVAL_METRICS_FILE,
            'agent_usage': AGENT_USAGE_FILE
        }
        
        if metric_type not in file_mapping:
            logger.error(f"Unknown metric type: {metric_type}")
            return []
        
        file_path = file_mapping[metric_type]
        
        if not os.path.exists(file_path):
            logger.warning(f"Metrics file does not exist: {file_path}")
            return []
        
        try:
            records = []
            with open(file_path, 'r') as f:
                for line in f:
                    if line.strip():
                        records.append(json.loads(line))
                        if len(records) >= limit:
                            break
            
            # Sort by timestamp, newest first
            records.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
            return records
            
        except Exception as e:
            logger.error(f"Error loading metrics: {str(e)}")
            return [] 