from respan_sdk.respan_types.experiment_types import (
    ExperimentType as Experiment,
    ListExperimentsResponse as ExperimentList,
    CreateExperimentRequest as ExperimentCreate,
    ExperimentColumnType,
    ExperimentRowType,
    ExperimentResultItemType,
    AddExperimentRowsRequest,
    RemoveExperimentRowsRequest,
    UpdateExperimentRowsRequest,
    AddExperimentColumnsRequest,
    RemoveExperimentColumnsRequest,
    UpdateExperimentColumnsRequest,
    RunExperimentRequest,
    RunExperimentEvalsRequest,
)

# Create a simple update type for experiment metadata
from respan_sdk.respan_types._internal_types import RespanBaseModel
from typing import Optional


class ExperimentUpdate(RespanBaseModel):
    """Update request for experiment metadata"""

    name: Optional[str] = None
    description: Optional[str] = None


__all__ = [
    "Experiment",
    "ExperimentList",
    "ExperimentCreate",
    "ExperimentUpdate",
    "ExperimentColumnType",
    "ExperimentRowType",
    "ExperimentResultItemType",
    "AddExperimentRowsRequest",
    "RemoveExperimentRowsRequest",
    "UpdateExperimentRowsRequest",
    "AddExperimentColumnsRequest",
    "RemoveExperimentColumnsRequest",
    "UpdateExperimentColumnsRequest",
    "RunExperimentRequest",
    "RunExperimentEvalsRequest",
]
