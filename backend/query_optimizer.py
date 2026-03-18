"""Advanced query optimization and analysis."""
import re
from typing import Dict, List, Any, Optional
from backend.logging_config import get_logger

logger = get_logger("query_optimizer")


class QueryOptimizer:
    """Optimize queries for better retrieval results."""
    
    def __init__(self):
        """Initialize query optimizer."""
        self.stopwords = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'from', 'is', 'are', 'was', 'were', 'be', 'been',
            'has', 'have', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
            'should', 'may', 'might', 'can', 'what', 'which', 'who', 'when', 'where',
            'why', 'how'
        }
        self.query_templates = [
            (r'what is.*\?', 'definition'),
            (r'how do.*\?', 'procedure'),
            (r'why.*\?', 'reason'),
            (r'when.*\?', 'temporal'),
            (r'where.*\?', 'location'),
            (r'compare.*', 'comparison'),
            (r'list.*', 'enumeration')
        ]
    
    def detect_query_type(self, query: str) -> str:
        """Detect the type of query.
        
        Args:
            query: The user's query.
            
        Returns:
            Query type classification.
        """
        query_lower = query.lower()
        
        for pattern, query_type in self.query_templates:
            if re.match(pattern, query_lower):
                return query_type
        
        return 'general'
    
    def extract_keywords(self, query: str) -> List[str]:
        """Extract important keywords from query.
        
        Args:
            query: The user's query.
            
        Returns:
            List of important keywords.
        """
        # Remove special characters and convert to lowercase
        cleaned = re.sub(r'[^a-z0-9\s]', '', query.lower())
        
        # Split into words
        words = cleaned.split()
        
        # Remove stopwords
        keywords = [w for w in words if w not in self.stopwords and len(w) > 2]
        
        return keywords
    
    def expand_query(self, query: str, expansion_terms: Optional[List[str]] = None) -> str:
        """Expand query with related terms for better retrieval.
        
        Args:
            query: Original query.
            expansion_terms: Optional additional terms to add.
            
        Returns:
            Expanded query.
        """
        expanded = query
        
        if expansion_terms:
            expanded = f"{query} {' '.join(expansion_terms)}"
        
        # Add query synonyms based on common patterns
        synonyms = {
            'discuss': ['talk about', 'explain'],
            'show': ['demonstrate', 'illustrate'],
            'create': ['build', 'develop'],
            'delete': ['remove', 'eliminate']
        }
        
        for word, syn_list in synonyms.items():
            if word in query.lower():
                expanded += ' ' + ' '.join(syn_list)
        
        logger.debug(f"Query expanded from '{query}' to '{expanded}'")
        return expanded
    
    def get_optimal_parameters(self, query: str) -> Dict[str, Any]:
        """Get optimal parameters for query based on type.
        
        Args:
            query: The user's query.
            
        Returns:
            Optimal retrieval parameters.
        """
        query_type = self.detect_query_type(query)
        keywords = self.extract_keywords(query)
        
        # Adjust parameters based on query type
        params = {
            'query_type': query_type,
            'keywords': keywords,
            'keyword_count': len(keywords),
        }
        
        # Adjust retrieval limit based on query type
        if query_type == 'enumeration':
            params['retrieval_limit'] = 10
        elif query_type == 'comparison':
            params['retrieval_limit'] = 8
        else:
            params['retrieval_limit'] = 5
        
        # Similarity threshold
        if query_type == 'definition':
            params['similarity_threshold'] = 0.5
        elif query_type == 'procedure':
            params['similarity_threshold'] = 0.4
        else:
            params['similarity_threshold'] = 0.3
        
        logger.info(f"Optimal parameters for '{query}': {params}")
        return params
    
    def validate_query(self, query: str) -> Dict[str, Any]:
        """Validate and analyze query quality.
        
        Args:
            query: The user's query.
            
        Returns:
            Validation results.
        """
        validation = {
            'valid': True,
            'issues': [],
            'suggestions': []
        }
        
        # Check query length
        if len(query) < 3:
            validation['valid'] = False
            validation['issues'].append('Query too short')
            validation['suggestions'].append('Please provide more details')
        elif len(query) > 500:
            validation['issues'].append('Query very long')
            validation['suggestions'].append('Consider breaking into multiple questions')
        
        # Check for keywords
        keywords = self.extract_keywords(query)
        if len(keywords) == 0:
            validation['issues'].append('No significant keywords found')
            validation['suggestions'].append('Query may not return good results')
        
        # Check for question mark
        if '?' not in query:
            validation['issues'].append('Query may not be a question')
            validation['suggestions'].append('Consider rephrasing as a question')
        
        return validation
    
    def preprocess_query(self, query: str) -> str:
        """Preprocess query for optimal retrieval.
        
        Args:
            query: Raw user query.
            
        Returns:
            Preprocessed query.
        """
        # Remove extra whitespace
        preprocessed = ' '.join(query.split())
        
        # Remove unnecessary punctuation at start/end
        preprocessed = preprocessed.strip('?.,!')
        
        # Normalize quotes
        preprocessed = preprocessed.replace('"', '').replace("'", '')
        
        # Convert to lowercase for processing (keep original for display)
        logger.debug(f"Query preprocessed: '{query}' -> '{preprocessed}'")
        
        return preprocessed


class QueryCache:
    """Cache for previously optimized queries."""
    
    def __init__(self):
        """Initialize query cache."""
        self.cache: Dict[str, Dict[str, Any]] = {}
    
    def get_optimization(self, query: str) -> Optional[Dict[str, Any]]:
        """Get cached optimization for query.
        
        Args:
            query: The query.
            
        Returns:
            Cached optimization or None.
        """
        normalized = query.lower().strip()
        return self.cache.get(normalized)
    
    def cache_optimization(self, query: str, optimization: Dict[str, Any]) -> None:
        """Cache optimization for query.
        
        Args:
            query: The query.
            optimization: Optimization data.
        """
        normalized = query.lower().strip()
        self.cache[normalized] = optimization
    
    def clear(self) -> None:
        """Clear the cache."""
        self.cache.clear()


# Global instances
_query_optimizer = None
_optimization_cache = None


def get_query_optimizer() -> QueryOptimizer:
    """Get or create the query optimizer singleton."""
    global _query_optimizer
    if _query_optimizer is None:
        _query_optimizer = QueryOptimizer()
    return _query_optimizer


def get_optimization_cache() -> QueryCache:
    """Get or create the optimization cache singleton."""
    global _optimization_cache
    if _optimization_cache is None:
        _optimization_cache = QueryCache()
    return _optimization_cache
