"""HTTP client interceptor to redirect Langfuse requests to Keywords AI."""

import httpx
import json
from typing import Optional


class KeywordsAIHTTPClient(httpx.Client):
    """Custom HTTP client that intercepts Langfuse ingestion requests."""
    
    def __init__(self, api_key: str, endpoint: str = "https://api.keywordsai.co/api/v1/traces/ingest", **kwargs):
        """Initialize the interceptor.
        
        Args:
            api_key: Keywords AI API key
            endpoint: Keywords AI traces endpoint
            **kwargs: Additional arguments for httpx.Client
        """
        super().__init__(**kwargs)
        self.api_key = api_key
        self.keywords_endpoint = endpoint
    
    def send(self, request: httpx.Request, *args, **kwargs) -> httpx.Response:
        """Intercept and redirect Langfuse ingestion requests to Keywords AI.
        
        Args:
            request: The HTTP request
            *args, **kwargs: Additional arguments
            
        Returns:
            HTTP response
        """
        # Check if this is a Langfuse ingestion request
        if b'/api/public/ingestion' in request.url.raw_path or b'/public/ingestion' in request.url.raw_path:
            try:
                # Parse Langfuse batch
                langfuse_batch = json.loads(request.content)
                
                # Transform to Keywords AI format
                keywords_logs = self._transform_langfuse_to_keywords(langfuse_batch)
                
                # Create new request to Keywords AI
                keywords_request = httpx.Request(
                    method="POST",
                    url=self.keywords_endpoint,
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                        "Accept": "application/json"
                    },
                    json=keywords_logs
                )
                
                response = super().send(keywords_request, *args, **kwargs)
                
                # Return a success response to Langfuse
                return httpx.Response(
                    status_code=200,
                    json={"status": "success"},
                    request=request
                )
                
            except Exception as e:
                # Return error response
                return httpx.Response(
                    status_code=500,
                    json={"error": str(e)},
                    request=request
                )
        
        # For non-ingestion requests, pass through normally
        return super().send(request, *args, **kwargs)
    
    def _transform_langfuse_to_keywords(self, langfuse_batch: dict) -> list:
        """Transform Langfuse batch format to Keywords AI format.
        
        Args:
            langfuse_batch: Langfuse batch data
            
        Returns:
            List of Keywords AI log entries
        """
        keywords_logs = []
        
        for event in langfuse_batch.get('batch', []):
            event_type = event.get('type')
            body = event.get('body', {})
            
            # Basic mapping - you'll need to expand this based on actual Langfuse format
            log = {
                "trace_unique_id": body.get('traceId') or body.get('id'),
                "span_unique_id": body.get('id'),
                "span_name": body.get('name', 'unknown'),
                "log_type": self._map_langfuse_type(event_type, body),
            }
            
            # Add optional fields if available
            if 'input' in body:
                log['input'] = json.dumps(body['input']) if not isinstance(body['input'], str) else body['input']
            if 'output' in body:
                log['output'] = json.dumps(body['output']) if not isinstance(body['output'], str) else body['output']
            if 'model' in body:
                log['model'] = body['model']
            if 'usage' in body:
                log['usage'] = body['usage']
            if 'startTime' in body:
                log['start_time'] = body['startTime']
            if 'endTime' in body or 'timestamp' in body:
                log['timestamp'] = body.get('endTime') or body.get('timestamp')
            if 'parentObservationId' in body:
                log['span_parent_id'] = body['parentObservationId']
            
            keywords_logs.append(log)
        
        return keywords_logs
    
    def _map_langfuse_type(self, event_type: Optional[str], body: dict) -> str:
        """Map Langfuse event type to Keywords AI log type.
        
        Args:
            event_type: Langfuse event type
            body: Event body
            
        Returns:
            Keywords AI log type
        """
        observation_type = body.get('type', '').lower()
        
        if 'generation' in observation_type:
            return 'generation'
        elif 'span' in observation_type:
            return 'tool' if body.get('parentObservationId') else 'workflow'
        else:
            return 'custom'
