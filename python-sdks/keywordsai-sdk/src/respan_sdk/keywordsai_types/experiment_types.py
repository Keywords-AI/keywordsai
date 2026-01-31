from enum import Enum
from typing import List, Dict, Any, Union, Literal, Optional
from pydantic import model_validator, ConfigDict
from ._internal_types import (
    KeywordsAIBaseModel,
    Message,
    FunctionTool,
    ToolChoice,
)
from ..utils.mixins import PreprocessDataMixin
from typing_extensions import TypedDict
from ..constants import UTC_EPOCH
from keywordsai_sdk.utils.data_processing.id_processing import generate_unique_id
from .generic_types import PaginatedResponseType
STATUS_TYPES = Literal[
    "ready", "running", "error", "stopped", "completed"
]  # Ready means ready to go


class ExperimentColumnType(KeywordsAIBaseModel, PreprocessDataMixin):
    """
    Represents a column (test configuration) in an experiment.
    Each column defines the parameters for one variant of the experiment.
    """

    id: str = ""
    model: str
    name: str
    temperature: float
    max_completion_tokens: int
    top_p: float
    frequency_penalty: float
    presence_penalty: float
    tools: List[FunctionTool] = []
    prompt_messages: List[Message] = []
    reasoning_effort: Optional[str] = None
    stream: bool = False
    tool_choice: Union[str, ToolChoice] = "auto"
    response_format: Union[str, Dict] = {"type": "text"}

    model_config = ConfigDict(extra="forbid")

    @model_validator(mode="before")
    @classmethod
    def _preprocess_data(cls, data):
        data = super()._preprocess_data(data)

        # Map messages to prompt_messages for backward compatibility
        if "messages" in data:
            data["prompt_messages"] = data.pop("messages")

        # Generate ID if not provided
        if not data.get("id"):
            data["id"] = generate_unique_id()

        return data


class ExperimentLLMInferenceMetrics(KeywordsAIBaseModel):
    """
    LLM inference metrics for a experiment cell
    """

    prompt_tokens: Optional[int] = None
    completion_tokens: Optional[int] = None
    total_tokens: Optional[int] = None
    prompt_tokens_details: Optional[Dict[str, Any]] = None
    completion_tokens_details: Optional[Dict[str, Any]] = None
    latency: Optional[float] = None

    model_config = ConfigDict(extra="allow")


class ExperimentResultItemType(KeywordsAIBaseModel, PreprocessDataMixin):
    """
    Represents a single result item within an experiment row.
    Contains the output and evaluation results for one column configuration.

    evaluation_result is a dictionary of evaluator_name to evaluation_result
    where eval_result is of type evaluation.models.EvalResult
    example:
    {
        eval_result.evaluator_name: EvalResultDetailSerializer(eval_result).data
    }

    output is a dictionary of completion message with tool calls
    {
        "role": "assistant",
        "content": "completion_message_value",
        # OR
        "tool_calls": [
            {
                "name": "tool_name",
                "arguments": "tool_arguments"
            }
        ]
    }
    """

    id: str = ""
    column_id: str = ""
    output: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    ran_at: str = UTC_EPOCH
    status: STATUS_TYPES = "ready"
    evaluation_result: Optional[Dict[str, Any]] = None
    llm_inference_metrics: Optional[ExperimentLLMInferenceMetrics] = None

    @model_validator(mode="before")
    @classmethod
    def _preprocess_data(cls, data):
        data = super()._preprocess_data(data)
        if not data.get("id"):
            data["id"] = generate_unique_id()
        return data


class ExperimentRowType(KeywordsAIBaseModel, PreprocessDataMixin):
    """
    Represents a row in an experiment.
    Each row contains input data and results for all columns.
    """

    id: str = ""
    input: Dict[str, Any] = {}
    status: STATUS_TYPES = "ready"
    results: List[Optional[ExperimentResultItemType]] = []
    ideal_output: Optional[str] = None

    @model_validator(mode="before")
    @classmethod
    def _preprocess_data(cls, data):
        data = super()._preprocess_data(data)
        if not data.get("id"):
            data["id"] = generate_unique_id()
        return data


class ExperimentRowV2Type(KeywordsAIBaseModel, PreprocessDataMixin):
    """
    A row in the experiment (V2 format)
    items is a map that maps the column id to the result
    inputs is a dictionary contains pairs of {variable_name: variable_value}
    id is the row id

    example:
    {
        "id": "123",
        "inputs": {
            "variable_name": "variable_value"
        },
        "ideal_output": "ideal_output_value",
        "items": {
            "column_id_1": {
                "output": "output_value",
                "ran_at": "2021-01-01T00:00:00Z",
                "status": "completed",
                "evaluation_result": {
                    "evaluator_id": {
                        "primary_score": 0.95,
                        "eval_class": "class_name_of_evaluator",
                    }
                }
            },
            "column_id_2": {
                "output": "output_value",
                "ran_at": "2021-01-01T00:00:00Z",
                "status": "completed",
                "evaluation_result": {
                    "evaluator_id": {
                        "primary_score": 0.95,
                        "eval_class": "class_name_of_evaluator",
                    }
                }
            }
            ...
        }
    }
    """

    id: str = ""
    inputs: Dict[str, Any] = {}
    items: Dict[str, ExperimentResultItemType] = {}
    ideal_output: Optional[str] = None

    @model_validator(mode="before")
    @classmethod
    def _preprocess_data(cls, data):
        data = super()._preprocess_data(data)
        if not data.get("id"):
            data["id"] = generate_unique_id()
        return data


class ExperimentType(KeywordsAIBaseModel, PreprocessDataMixin):
    """
    Main experiment type representing the complete experiment structure.
    Based on the Django Experiment model.
    """

    id: str = ""
    column_count: int = 0
    columns: List[ExperimentColumnType] = []
    created_at: Optional[str] = None
    created_by: Optional[Union[Dict[str, Any], int, str]] = (
        None  # APIUser reference, could be a foreign key id or a serialized object
    )
    name: str
    organization: Optional[Union[Dict[str, Any], int, str]] = (
        None  # Organization reference, could be a foreign key id or a serialized object
    )
    row_count: int = 0
    rows: List[ExperimentRowType] = []
    status: str = ""
    test_id: str = ""
    updated_at: Optional[str] = None
    updated_by: Optional[Union[Dict[str, Any], int, str]] = (
        None  # APIUser reference, could be a foreign key id or a serialized object
    )
    variables: List[str] = []
    variable_definitions: List[Dict[str, Any]] = []
    starred: bool = False
    tags: List[Union[Dict[str, Any], int, str]] = (
        []
    )  # ExperimentTag references, could be a foreign key id or a serialized object
    description: str = ""

    @model_validator(mode="before")
    @classmethod
    def _preprocess_data(cls, data):
        data = super()._preprocess_data(data)
        if not data.get("id"):
            data["id"] = generate_unique_id()
        return data


# Request/Response types for API endpoints
class CreateExperimentRequest(KeywordsAIBaseModel):
    """Request payload for creating an experiment"""

    columns: List[ExperimentColumnType]
    rows: List[ExperimentRowType] = []
    name: str
    description: str = ""


ListExperimentsResponse = PaginatedResponseType[ExperimentType]


class AddExperimentRowsRequest(KeywordsAIBaseModel):
    """Request payload for adding rows to an experiment"""

    rows: List[ExperimentRowType]


class RemoveExperimentRowsRequest(KeywordsAIBaseModel):
    """Request payload for removing rows from an experiment"""

    rows: List[str]  # List of row IDs


class UpdateExperimentRowsRequest(KeywordsAIBaseModel):
    """Request payload for updating experiment rows"""

    rows: List[ExperimentRowType]


class AddExperimentColumnsRequest(KeywordsAIBaseModel):
    """Request payload for adding columns to an experiment"""

    columns: List[ExperimentColumnType]


class RemoveExperimentColumnsRequest(KeywordsAIBaseModel):
    """Request payload for removing columns from an experiment"""

    columns: List[str]  # List of column IDs


class UpdateExperimentColumnsRequest(KeywordsAIBaseModel):
    """Request payload for updating experiment columns"""

    columns: List[ExperimentColumnType]


class RunExperimentRequest(KeywordsAIBaseModel):
    """Request payload for running an experiment"""

    columns: Optional[List[ExperimentColumnType]] = None


class RunExperimentEvalsRequest(KeywordsAIBaseModel):
    """Request payload for running experiment evaluations"""

    evaluator_slugs: List[str]


# Legacy types for backward compatibility
class Columns(KeywordsAIBaseModel):
    """Legacy wrapper for columns"""

    columns: List[ExperimentColumnType]


class Rows(KeywordsAIBaseModel):
    """Legacy wrapper for rows"""

    rows: List[ExperimentRowType]


class EditorType(KeywordsAIBaseModel):
    """Editor information"""

    id: int
    name: str


class TestCaseType(KeywordsAIBaseModel, PreprocessDataMixin):
    """Test case definition"""

    description: Optional[str] = None
    name: Optional[str] = None
    headers: List[str] = []
    rows: List[Dict[str, Union[str, int, None]]] = []

    @model_validator(mode="after")
    def validate_rows(self):
        for i, row in enumerate(self.rows):
            headers = set(self.headers)
            row_headers = set(row.keys())
            if row_headers != headers:
                raise ValueError(
                    f"Row {i} headers do not match test headers: {row_headers} != {headers}"
                )
        return self


class TestsetColumnDefinition(KeywordsAIBaseModel):
    """Column definition for testsets"""

    field: str
    width: Optional[float] = None
    mapped_name: Optional[str] = None
    is_hidden: Optional[bool] = False
    type: Optional[Literal["text", "image_url", "note"]] = "text"

    model_config = ConfigDict(extra="allow")


class TestsetOperationType(Enum):
    """Types of operations that can be performed on testsets"""

    INSERT_ROWS = "insert_rows"
    UPDATE_ROWS = "update_rows"
    DELETE_ROWS = "delete_rows"
    REORDER_ROWS = "reorder_rows"


class TestsetRowData(TypedDict, total=False):
    """Data structure for testset row operations"""

    row_index: Optional[int]
    height: Optional[float]
    # This is a row. Format: {"column_name": "column_value", "column_name2": "column_value2"}
    row_data: Dict[str, Union[str, int, None, float, bool]]


class TestsetRowOperationsPayload(KeywordsAIBaseModel):
    """Payload for testset row operations"""

    testset_rows: List[TestsetRowData]
