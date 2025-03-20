from keywordsai_sdk.keywordsai_types._internal_types import KeywordsAIBaseModel
from pydantic import field_validator, model_validator
from typing import List, Union, Dict, Any, Literal, Callable, TypedDict
from keywordsai_sdk.keywordsai_types._internal_types import (
    EvalInputs,
    Message,
    EvaluatorToRun
)
from keywordsai_sdk.keywordsai_types.generic_types import ParamType
from keywordsai_sdk.constants import DEFAULT_EVAL_LLM_ENGINE, LLM_ENGINE_FIELD_NAME
import random
import json

Operator = Literal[
    "eq", "neq", "gt", "gte", "lt", "lte", "contains", "starts_with", "ends_with"
]

ValueType = Union[str, float, int, bool, List, Dict, None]
FilterType = Literal[
    "environment",
    "customer_identifier",
    "evaluation_identifier",
    "prompt_id",
    "user_query",
]

FieldInputType = Literal[
    "select",
    "input",
    "input_text",
    "input_number",
    "input_date",
    "textarea",
    "searchable_select",
    "checkbox",
    "radio",
    "tag_input",
    "input_array",
    "textarea_array",  # This is for array of strings
    "input_arrays",  # This is for array of arrays of strings
    "textarea_arrays",  # This is for array of arrays of strings
    "json"
]


class ChoiceType(KeywordsAIBaseModel):
    name: str
    value: ValueType


class BaseActionType(KeywordsAIBaseModel):
    field: str
    operator: Operator
    value: ValueType = None
    field_type: FieldInputType = "input"
    choices: List[ChoiceType] = []

    @model_validator(mode="after")
    def validate_value(self):
        if self.choices and self.value is not None:
            if self.value not in [choice.value for choice in self.choices]:
                raise ValueError(f"Value {self.value} is not a valid choice")
        if self.field_type == "input_number" and self.value:
            try:
                self.value = float(self.value)
            except ValueError:
                raise ValueError(f"Value {self.value} is not a valid number")
        return self

class FilterAction(BaseActionType):
    field: FilterType
    pass
class ConditionAction(BaseActionType):
    param_info: Union[ParamType, None] = None
    pass


EvalType = Literal["llm", "function", "human", "grounded"]
EvalCategory = Literal["ragas", "custom"]


class FieldType(KeywordsAIBaseModel):
    name: str
    display_name: str
    type: FieldInputType = "input"
    description: str = ""
    required: bool = False
    default_value: ValueType = None
    placeholder: str = ""
    choices: List[ChoiceType] = []
    value: ValueType = None

    @model_validator(mode="after")
    def validate_value(self):
        if self.choices and self.value is not None:
            if self.value not in [choice.value for choice in self.choices]:
                raise ValueError(f"Value {self.value} is not a valid choice")
        if self.type == "input_number" and self.value:
            try:
                self.value = float(self.value)
            except ValueError:
                raise ValueError(f"Value {self.value} is not a valid number")
            
        if self.type == "json" and self.value and not isinstance(self.value, dict):
            
            try:
                self.value = json.loads(self.value)
            except json.JSONDecodeError:
                raise ValueError(f"Value {self.value} is not a valid JSON")
        return self

    



class ScoreMapping(KeywordsAIBaseModel):
    primary_score: Union[str, None] = None
    secondary_score: Union[str, None] = None
    tertiary_score: Union[str, None] = None
    quaternary_score: Union[str, None] = None

    @property
    def reverse_mapping(self):
        return {v: k for k, v in self.model_dump().items() if v is not None}

class ScoreMappingDict(TypedDict):
    primary_score: Union[str, None] = None
    secondary_score: Union[str, None] = None
    tertiary_score: Union[str, None] = None
    quaternary_score: Union[str, None] = None


class BaseEvalFormType(KeywordsAIBaseModel):
    eval_class: str
    type: EvalType
    note: str = ""
    display_name: str  # This is just the title of the form
    description: str
    special_fields: List[FieldType] = []
    required_fields: List[FieldType] = (
        []
    )  # Just tags that tells users what are needed to run this eval, not fields on the form
    inference_filters: List[FilterAction] = []
    allow_conditions: bool = True
    conditions: List[ConditionAction] = []
    score_mapping: ScoreMapping = None
    category: EvalCategory = "custom"

    def validate_required_inputs(self, inputs: Dict[str, ValueType]):
        for field in self.required_fields:
            if field.name not in inputs:
                raise ValueError(
                    f"Field {field.name} is required but not found in inputs"
                )
            field_validator = getattr(self, f"validate_{field.name}", None)
            if isinstance(field_validator, Callable):
                field_validator(inputs[field.name])
        return self


class FilterValue(KeywordsAIBaseModel):
    field: FilterType
    value: ValueType


class EvalParamsDict(TypedDict):
    completion_messages: List[Message]
    eval_inputs: EvalInputs = {}
    prompt_messages: List[Message]
    last_n_messages: int = 1
    filter_values: List[FilterValue]


class EvalParams(KeywordsAIBaseModel):
    evaluation_identifier: str = ""
    completion_message: Message
    eval_inputs: EvalInputs = {}
    prompt_messages: List[Message]
    last_n_messages: int = 1
    filter_values: List[FilterValue] = []
    is_paid_user: bool = False
    evaluators: List[EvaluatorToRun] = [] # The list of evaluator slugs to run

    def model_dump(self, *args, **kwargs) -> "EvalParamsDict":
        kwargs["exclude_none"] = True
        return super().model_dump(*args, **kwargs)
    



# EvalInputsDict = TypedDict('EvalInputsDict', **{k: v.outer_type_ for k, v in EvalInputs.model_fields.items()})
class EvalCost(KeywordsAIBaseModel):
    cost: float
    input_tokens: Union[int, None] = None
    output_tokens: Union[int, None] = None
    model: Union[str, None] = None

class EvalResultType(KeywordsAIBaseModel):
    scores: Dict[str, Any]
    cost: EvalCost
    passed: bool

class EvalErrorType(KeywordsAIBaseModel):
    error: str
    error_type: str


class EvalConfigurations(KeywordsAIBaseModel):
    id: str
    organization_id: int
    model: Union[str, None] = None
    enabled: bool = False
    sample_percentage: Union[float, None] = None
    eval_class: str
    configurations: BaseEvalFormType
    name: str = ""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.load_configs()

    @field_validator("model")
    def validate_model(cls,value):
        if not value:
            return DEFAULT_EVAL_LLM_ENGINE
        return value

    def load_configs(self):
        configs = self.configurations
        if configs.type == "llm":
            llm_engine_field = next(
                (
                    field
                    for field in configs.special_fields
                    if field.name == LLM_ENGINE_FIELD_NAME
                ),
                None,
            )
            if llm_engine_field:
                self.model = llm_engine_field.value

    def _check_conditions(self, conditions: List[BaseActionType], values: Dict[str, Any]) -> bool:
        for condition in conditions:
            operator = condition.operator
            field_value = condition.value
            field_name = condition.field
            value = values.get(field_name)

            # Don't touch. As long as it is falsely, we will skip (not necessarily None)
            if not field_value:
                continue

            if operator == "eq":
                if field_value != value:
                    return False
            elif operator == "neq":
                if field_value == value:
                    return False
            elif operator in ["gt", "gte", "lt", "lte"]:
                if not isinstance(value, (int, float)) or not isinstance(field_value, (int, float)):
                    return False
                if operator == "gt" and not (value > field_value):
                    return False
                elif operator == "gte" and not (value >= field_value):
                    return False
                elif operator == "lt" and not (value < field_value):
                    return False
                elif operator == "lte" and not (value <= field_value):
                    return False
            elif operator == "contains":
                if not (isinstance(value, str) and isinstance(field_value, str) and field_value in value):
                    return False
            elif operator == "starts_with":
                if not (isinstance(value, str) and isinstance(field_value, str) and value.startswith(field_value)):
                    return False
            elif operator == "ends_with":
                if not (isinstance(value, str) and isinstance(field_value, str) and value.endswith(field_value)):
                    return False

        return True

    def running_conditions_met(self, inputs: EvalParams, hard_override: Union[bool, None] = None):
        if hard_override is not None:
            return hard_override
        filter_values = {
            filter_value.field: filter_value.value
            for filter_value in inputs.filter_values
        }
        if not self._check_conditions(self.configurations.inference_filters, filter_values):
            return False

        if self.sample_percentage is not None and self.sample_percentage < random.randint(1, 100):
            return False
        
        return self.enabled

    def passing_conditions_met(self, results: Dict[str, Any], hard_override: Union[bool, None] = None):
        if hard_override is not None:
            return hard_override
        
        return self._check_conditions(self.configurations.conditions, results)

    class Config:
        from_attributes = True
