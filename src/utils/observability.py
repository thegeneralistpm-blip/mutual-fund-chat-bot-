import time
import functools
import logging
import json
from typing import Any, Dict

logger = logging.getLogger("observability")
logger.setLevel(logging.INFO)

# In production, this would send data to Langfuse, Prometheus, or Datadog
class Observability:
    """Tracks performance metrics and token usage for the chatbot."""

    @staticmethod
    def track_latency(func):
        """Decorator to track the latency of a function call."""
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            result = func(*args, **kwargs)
            duration = time.time() - start_time
            
            # Simple log of the metric
            metric = {
                "function": func.__name__,
                "latency_seconds": round(duration, 3),
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }
            logger.info(f"METRIC: {json.dumps(metric)}")
            return result
        return wrapper

    @staticmethod
    def log_event(event_name: str, metadata: Dict[str, Any]):
        """Logs a custom event with metadata."""
        log_entry = {
            "event": event_name,
            "metadata": metadata,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        logger.info(f"EVENT: {json.dumps(log_entry)}")
