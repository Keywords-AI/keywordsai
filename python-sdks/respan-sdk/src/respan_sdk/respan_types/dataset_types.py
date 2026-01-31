from respan_sdk.respan_types.base_types import RespanBaseModel
from typing import Optional, List, Dict, Any, Union
from datetime import datetime
from respan_sdk.constants.dataset_constants import (
    DatasetType,
    DatasetStatus,
    DatasetLLMRunStatus,
    DATASET_TYPE_LLM,
    DATASET_STATUS_INITIALIZING,
    DATASET_LLM_RUN_STATUS_PENDING,
)
from respan_sdk.respan_types.filter_types import FilterParamDict
from respan_sdk.respan_types.generic_types import PaginatedResponseType


class Dataset(RespanBaseModel):
    """Dataset model matching Django Dataset model"""

    id: str
    name: str
    type: DatasetType = DATASET_TYPE_LLM
    description: str = ""
    created_at: datetime
    running_progress: float = 0.0
    running_status: DatasetLLMRunStatus = DATASET_LLM_RUN_STATUS_PENDING
    running_at: Optional[datetime] = None
    updated_at: datetime
    updated_by: Optional[Union[Dict[str, Any], int, str]] = (
        None  # APIUser reference, could be a foreign key id or a serialized object
    )
    organization: Union[
        Dict[str, Any], int, str
    ]  # Organization reference, could be a foreign key id or a serialized object
    initial_log_filters: FilterParamDict = {}
    log_ids: List[str] = []
    unique_organization_ids: List[str] = []
    timestamps: List[datetime] = []
    log_count: int = 0
    evaluator: Optional[str] = None  # Evaluator ID
    status: DatasetStatus = DATASET_STATUS_INITIALIZING
    completed_annotation_count: Optional[int] = None  # Read-only field


class DatasetCreate(RespanBaseModel):
    """Dataset creation request"""

    name: str
    description: str = ""
    type: DatasetType = DATASET_TYPE_LLM
    sampling: Optional[int] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    initial_log_filters: FilterParamDict = {}


class DatasetUpdate(RespanBaseModel):
    """Dataset update request"""

    name: Optional[str] = None
    description: Optional[str] = None


class DatasetList(RespanBaseModel):
    """Dataset list response"""

    results: List[Dataset]
    count: Optional[int] = None
    next: Optional[str] = None
    previous: Optional[str] = None


class LogManagementRequest(RespanBaseModel):
    """Request for adding/removing logs from dataset"""

    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    filters: FilterParamDict


class EvalRunRequest(RespanBaseModel):
    """Request to run evaluation on dataset"""

    evaluator_slugs: List[str]


class EvalReport(RespanBaseModel):
    """Evaluation report response"""

    id: str
    dataset_id: str
    evaluator_slugs: List[str]
    status: str
    created_at: datetime
    updated_at: datetime
    results: Optional[Dict[str, Any]] = None


class EvalReportList(RespanBaseModel):
    """Evaluation report list response"""

    results: List[EvalReport]
    count: Optional[int] = None
    next: Optional[str] = None
    previous: Optional[str] = None
