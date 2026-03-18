"""Analytics and monitoring for RAG system."""
import time
from datetime import datetime, timedelta
from typing import Dict, Any, List
from collections import defaultdict
from backend.logging_config import get_logger

logger = get_logger("analytics")


class RAGAnalytics:
    """Track metrics and analytics for the RAG system."""
    
    def __init__(self):
        """Initialize analytics tracker."""
        self.query_metrics = []
        self.retrieval_metrics = defaultdict(list)
        self.generation_metrics = []
        self.error_count = 0
        self.total_queries = 0
        self.start_time = datetime.now()
    
    def record_query_start(self) -> float:
        """Record the start of query processing.
        
        Returns:
            Start timestamp for latency calculation.
        """
        return time.time()
    
    def record_query_end(
        self,
        start_time: float,
        question: str,
        success: bool,
        retrieved_count: int = 0
    ) -> Dict[str, Any]:
        """Record metrics for a completed query.
        
        Args:
            start_time: Query start timestamp.
            question: The user's question.
            success: Whether query was successful.
            retrieved_count: Number of documents retrieved.
            
        Returns:
            Metric data for logging.
        """
        latency = time.time() - start_time
        self.total_queries += 1
        
        if not success:
            self.error_count += 1
        
        metric = {
            "timestamp": datetime.now().isoformat(),
            "latency_ms": latency * 1000,
            "question_length": len(question),
            "retrieved_count": retrieved_count,
            "success": success
        }
        
        self.query_metrics.append(metric)
        logger.info(f"Query metrics: {metric}")
        return metric
    
    def record_retrieval_metrics(
        self,
        query: str,
        results_count: int,
        retrieval_time: float,
        top_score: float
    ) -> None:
        """Record vector search metrics.
        
        Args:
            query: The query text.
            results_count: Number of results retrieved.
            retrieval_time: Time taken for retrieval in seconds.
            top_score: Similarity score of top result.
        """
        metric = {
            "timestamp": datetime.now().isoformat(),
            "results_count": results_count,
            "retrieval_time_ms": retrieval_time * 1000,
            "top_score": top_score
        }
        self.retrieval_metrics[query].append(metric)
        logger.info(f"Retrieval metrics for '{query}': {metric}")
    
    def record_generation_metrics(
        self,
        prompt_tokens: int,
        completion_tokens: int,
        generation_time: float
    ) -> None:
        """Record LLM generation metrics.
        
        Args:
            prompt_tokens: Tokens in prompt.
            completion_tokens: Tokens in response.
            generation_time: Time taken to generate in seconds.
        """
        metric = {
            "timestamp": datetime.now().isoformat(),
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": prompt_tokens + completion_tokens,
            "generation_time_ms": generation_time * 1000
        }
        self.generation_metrics.append(metric)
        logger.info(f"Generation metrics: {metric}")
    
    def get_system_stats(self) -> Dict[str, Any]:
        """Get system-wide statistics.
        
        Returns:
            Dictionary with system metrics.
        """
        uptime = datetime.now() - self.start_time
        
        if self.query_metrics:
            avg_latency = sum(m['latency_ms'] for m in self.query_metrics) / len(self.query_metrics)
            success_rate = (self.total_queries - self.error_count) / self.total_queries * 100
        else:
            avg_latency = 0
            success_rate = 0
        
        if self.generation_metrics:
            avg_tokens = sum(m['total_tokens'] for m in self.generation_metrics) / len(self.generation_metrics)
        else:
            avg_tokens = 0
        
        return {
            "uptime_seconds": uptime.total_seconds(),
            "total_queries": self.total_queries,
            "successful_queries": self.total_queries - self.error_count,
            "failed_queries": self.error_count,
            "success_rate_percent": success_rate,
            "avg_query_latency_ms": avg_latency,
            "total_retrieved_documents": sum(m.get('retrieved_count', 0) for m in self.query_metrics),
            "avg_tokens_per_generation": avg_tokens,
            "total_generations": len(self.generation_metrics)
        }
    
    def get_recent_queries(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent query metrics.
        
        Args:
            limit: Number of recent queries to return.
            
        Returns:
            List of recent query metrics.
        """
        return self.query_metrics[-limit:] if self.query_metrics else []
    
    def get_performance_report(self) -> Dict[str, Any]:
        """Generate a comprehensive performance report.
        
        Returns:
            Detailed performance metrics.
        """
        return {
            "system_stats": self.get_system_stats(),
            "recent_queries": self.get_recent_queries(5),
            "retrieval_summary": {
                k: {
                    "query_count": len(v),
                    "avg_results": sum(m['results_count'] for m in v) / len(v) if v else 0,
                    "avg_time_ms": sum(m['retrieval_time_ms'] for m in v) / len(v) if v else 0
                }
                for k, v in self.retrieval_metrics.items()
            }
        }


# Global analytics instance
_analytics = None


def get_analytics() -> RAGAnalytics:
    """Get or create the analytics singleton."""
    global _analytics
    if _analytics is None:
        _analytics = RAGAnalytics()
    return _analytics
