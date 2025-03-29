"""
Prometheus client for querying metrics.
"""

import requests
from config.settings import PROMETHEUS_URL


def run_promql_query(query):
    """
    Run a PromQL query against the Prometheus server.
    
    Args:
        query (str): The PromQL query to execute
        
    Returns:
        list: List of results from the query
    """
    try:
        response = requests.get(f"{PROMETHEUS_URL}/api/v1/query", params={"query": query})
        response.raise_for_status()
        return response.json().get("data", {}).get("result", [])
    except requests.exceptions.RequestException as e:
        print(f"Error querying Prometheus: {e}")
        return []


def get_metric_value(query, default=None):
    """
    Get a single metric value from a PromQL query.
    
    Args:
        query (str): The PromQL query to execute
        default: Default value to return if query fails
        
    Returns:
        float: The metric value or default if not found
    """
    results = run_promql_query(query)
    return float(results[0]['value'][1]) if results else default