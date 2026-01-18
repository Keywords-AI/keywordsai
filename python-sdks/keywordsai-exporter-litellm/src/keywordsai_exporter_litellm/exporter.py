"""Keywords AI LiteLLM Integration.

KeywordsAILiteLLMCallback - LiteLLM-native callback class for sending logs to Keywords AI.
"""

import json
import logging
import os
import threading
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import requests

logger = logging.getLogger(__name__)

DEFAULT_ENDPOINT = "https://api.keywordsai.co/api/v1/traces/ingest"


class KeywordsAILiteLLMCallback:
    """LiteLLM callback that sends logs to Keywords AI.
    
    Usage:
        callback = KeywordsAILiteLLMCallback(api_key="...")
        litellm.success_callback = [callback.log_success_event]
        litellm.failure_callback = [callback.log_failure_event]
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        endpoint: Optional[str] = None,
        timeout: int = 10,
    ):
        self.api_key = api_key or os.getenv("KEYWORDSAI_API_KEY")
        self.endpoint = endpoint or os.getenv("KEYWORDSAI_ENDPOINT", DEFAULT_ENDPOINT)
        self.timeout = timeout
        if not self.api_key:
            logger.warning("Keywords AI API key not provided")
    
    def log_success_event(
        self, kwargs: Dict, response_obj: Any, start_time: datetime, end_time: datetime
    ) -> None:
        """Log successful completion."""
        self._log_event(kwargs, response_obj, start_time, end_time, error=None)
    
    async def async_log_success_event(
        self, kwargs: Dict, response_obj: Any, start_time: datetime, end_time: datetime
    ) -> None:
        """Async log successful completion."""
        threading.Thread(
            target=self._log_event, args=(kwargs, response_obj, start_time, end_time, None)
        ).start()
    
    def log_failure_event(
        self, kwargs: Dict, response_obj: Any, start_time: datetime, end_time: datetime
    ) -> None:
        """Log failed completion."""
        error = kwargs.get("exception") or kwargs.get("traceback_exception")
        self._log_event(kwargs, response_obj, start_time, end_time, error=error)
    
    async def async_log_failure_event(
        self, kwargs: Dict, response_obj: Any, start_time: datetime, end_time: datetime
    ) -> None:
        """Async log failed completion."""
        error = kwargs.get("exception") or kwargs.get("traceback_exception")
        threading.Thread(
            target=self._log_event, args=(kwargs, response_obj, start_time, end_time, error)
        ).start()
    
    def _log_event(
        self,
        kwargs: Dict,
        response_obj: Any,
        start_time: datetime,
        end_time: datetime,
        error: Optional[Exception],
    ) -> None:
        """Send event to Keywords AI."""
        if not self.api_key:
            return
        
        try:
            model = kwargs.get("model") or kwargs.get("litellm_params", {}).get("model")
            messages = kwargs.get("messages", [])
            metadata = kwargs.get("litellm_params", {}).get("metadata", {}) or {}
            kw_params = metadata.get("keywordsai_params", {})
            
            payload = {
                "trace_unique_id": kw_params.get("trace_id") or uuid.uuid4().hex,
                "span_unique_id": kw_params.get("span_id") or uuid.uuid4().hex[:16],
                "span_name": kw_params.get("span_name", "litellm.completion"),
                "span_workflow_name": kw_params.get("workflow_name", "litellm"),
                "log_type": "generation",
                "timestamp": end_time.astimezone(timezone.utc).isoformat(),
                "start_time": start_time.astimezone(timezone.utc).isoformat(),
                "latency": (end_time - start_time).total_seconds(),
                "model": model,
                "input": json.dumps(messages),
                "stream": kwargs.get("stream", False),
            }
            
            if parent_id := kw_params.get("parent_span_id"):
                payload["span_parent_id"] = parent_id
            if kwargs.get("tools"):
                payload["tools"] = kwargs["tools"]
            if kwargs.get("tool_choice"):
                payload["tool_choice"] = kwargs["tool_choice"]
            
            if error:
                payload["status"] = "error"
                payload["error_message"] = str(error)
            else:
                payload["status"] = "success"
                if response_obj:
                    self._add_response_data(payload, response_obj)
            
            self._add_keywordsai_params(payload, kw_params)
            self._send([payload])
        except Exception as e:
            logger.error(f"Keywords AI logging error: {e}")
    
    def _add_response_data(self, payload: Dict, response_obj: Any) -> None:
        """Add response data to payload."""
        resp = self._extract_response(response_obj)
        if choices := resp.get("choices", []):
            payload["output"] = json.dumps(choices[0].get("message", {}))
        if usage := resp.get("usage", {}):
            payload["usage"] = {
                "prompt_tokens": usage.get("prompt_tokens"),
                "completion_tokens": usage.get("completion_tokens"),
                "total_tokens": usage.get("total_tokens"),
            }
    
    def _add_keywordsai_params(self, payload: Dict, kw_params: Dict) -> None:
        """Add Keywords AI specific params to payload."""
        extra_meta = {}
        
        if "customer_identifier" in kw_params:
            payload["customer_identifier"] = kw_params["customer_identifier"]
        if cp := kw_params.get("customer_params"):
            if isinstance(cp, dict):
                payload["customer_identifier"] = cp.get("customer_identifier")
                extra_meta.update({f"customer_{k}": v for k, v in cp.items() if k != "customer_identifier"})
        if "thread_identifier" in kw_params:
            payload["thread_identifier"] = kw_params["thread_identifier"]
        if m := kw_params.get("metadata"):
            if isinstance(m, dict):
                extra_meta.update(m)
        
        excluded = (
            "customer_identifier", "customer_params", "thread_identifier", "metadata",
            "workflow_name", "trace_id", "span_id", "parent_span_id", "span_name"
        )
        extra_meta.update({k: v for k, v in kw_params.items() if k not in excluded})
        
        if extra_meta:
            payload["metadata"] = extra_meta
    
    def _extract_response(self, response_obj: Any) -> Dict:
        """Extract dict from response object."""
        if hasattr(response_obj, "model_dump"):
            return response_obj.model_dump(mode="json")
        if hasattr(response_obj, "dict"):
            return response_obj.dict()
        if isinstance(response_obj, dict):
            return response_obj
        return {}
    
    def send_workflow_span(
        self,
        trace_id: str,
        span_id: str,
        workflow_name: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        parent_span_id: Optional[str] = None,
        customer_identifier: Optional[str] = None,
        thread_identifier: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        input_data: Optional[Any] = None,
        output_data: Optional[Any] = None,
    ) -> None:
        """Send a workflow span to Keywords AI."""
        if not self.api_key:
            return
        
        try:
            now = datetime.now(timezone.utc)
            start = start_time or now
            end = end_time or now
            
            payload = {
                "trace_unique_id": trace_id,
                "span_unique_id": span_id,
                "span_name": workflow_name,
                "span_workflow_name": workflow_name,
                "log_type": "workflow",
                "timestamp": end.isoformat(),
                "start_time": start.isoformat(),
                "latency": (end - start).total_seconds() if end_time else 0.0,
                "status": "success",
            }
            
            if parent_span_id:
                payload["span_parent_id"] = parent_span_id
            if customer_identifier:
                payload["customer_identifier"] = customer_identifier
            if thread_identifier:
                payload["thread_identifier"] = thread_identifier
            if metadata:
                payload["metadata"] = metadata
            if input_data:
                payload["input"] = input_data if isinstance(input_data, str) else json.dumps(input_data)
            if output_data:
                payload["output"] = output_data if isinstance(output_data, str) else json.dumps(output_data)
            
            self._send([payload])
        except Exception as e:
            logger.error(f"Keywords AI workflow span error: {e}")
    
    def _send(self, payloads: List[Dict[str, Any]]) -> None:
        """Send payloads to Keywords AI."""
        try:
            response = requests.post(
                self.endpoint,
                json=payloads,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                timeout=self.timeout,
            )
            if response.status_code != 200:
                logger.warning(f"Keywords AI error: {response.status_code}")
        except Exception as e:
            logger.error(f"Keywords AI request error: {e}")
