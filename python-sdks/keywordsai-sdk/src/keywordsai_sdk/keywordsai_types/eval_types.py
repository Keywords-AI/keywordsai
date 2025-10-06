from keywordsai_sdk.keywordsai_types._internal_types import KeywordsAIBaseModel
from pydantic import field_validator, model_validator, ConfigDict
from typing import List, Union, Dict, Any, Literal, Callable, Optional
from typing_extensions import TypedDict
from keywordsai_sdk.keywordsai_types._internal_types import (
    Message,
)
from keywordsai_sdk.constants import DEFAULT_EVAL_LLM_ENGINE, LLM_ENGINE_FIELD_NAME
import json

from keywordsai_sdk.keywordsai_types.mixin_types.filter_mixin import (
    BaseFilterMixinPydantic,
)
from keywordsai_sdk.keywordsai_types.monitoring_types import ConditionParams
from keywordsai_sdk.utils.mixins import PreprocessEvalConfigurationsMixin, PreprocessEvalFormMixin

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
    "json",
    "code",
]


class EvalInputs(TypedDict, total=False):
    # Default inputs, automatically populated by Keywords AI
    llm_input: str = (
        ""  # Reserved key, automatically populated by the `messages` parameter
    )
    llm_output: str = (
        ""  # Reserved key, automatically populated by the LLM's response.message
    )
    input: str = ""  # As of 2025-07-29, this will be the replacement for llm_input
    output: str = ""  # As of 2025-07-29, this will be the replacement for llm_output

    # LLM output related inputs
    ideal_output: Optional[str] = (
        None  # Reserved, but need to be provided, default null and ignored
    )

    # RAG related inputs
    ground_truth: Optional[str] = (
        None  # Reserved, but need to be provided, default null and ignored
    )
    retrieved_contexts: Optional[List[str]] = (
        None  # Reserved, but need to be provided, default null and ignored
    )
    ideal_contexts: Optional[List[str]] = (
        None  # Reserved, but need to be provided, default null and ignored
    )

    model_config = ConfigDict(extra="allow")


class ChoiceType(KeywordsAIBaseModel):
    name: str
    value: ValueType


EvalType = Literal["llm", "function", "human", "grounded"]
EvalCategory = Literal["ragas", "custom", "keywordsai"]


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
    # region: Fields for different types of results
    primary_score: Union[str, None] = None
    string_result: Union[str, None] = None
    boolean_result: Union[str, None] = None
    # endregion

    # region: reserved fields for additional numeric scores
    secondary_score: Union[str, None] = None
    tertiary_score: Union[str, None] = None
    quaternary_score: Union[str, None] = None
    # endregion

    @property
    def reverse_mapping(self):
        return {v: k for k, v in self.model_dump().items() if v is not None}


class ScoreMappingDict(TypedDict):
    primary_score: Union[str, None] = None
    secondary_score: Union[str, None] = None
    tertiary_score: Union[str, None] = None
    quaternary_score: Union[str, None] = None


class BaseEvalFormType(PreprocessEvalFormMixin, KeywordsAIBaseModel):
    eval_class: str
    type: EvalType
    note: str = ""  # Note to the user from us developers
    display_name: str  # This is just the title of the form
    description: str  # User specified description
    special_fields: List[FieldType] = []
    required_fields: List[FieldType] = (
        []
    )  # Just tags that tells users what are needed to run this eval, not fields on the form
    passing_conditions: List[BaseFilterMixinPydantic] = []
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

    model_config = ConfigDict(extra="allow")


class FilterValue(KeywordsAIBaseModel):
    field: FilterType
    value: ValueType


class EvalParamsDict(TypedDict):
    completion_messages: List[Message]
    eval_inputs: EvalInputs = {}
    prompt_messages: List[Message]
    last_n_messages: int = 1
    filter_values: List[FilterValue]


class EvaluatorToRun(KeywordsAIBaseModel):
    evaluator_slug: str
    run_condition: Optional[ConditionParams] = None
    # TODO: other controlling parameters


class EvalParams(KeywordsAIBaseModel):
    evaluation_identifier: str = ""
    completion_message: Message = Message(role="user", content="")
    eval_inputs: EvalInputs = {}
    prompt_messages: List[Message] = []
    last_n_messages: int = 1
    filter_values: List[FilterValue] = []
    is_paid_user: bool = False
    evaluators: List[EvaluatorToRun] = []  # The list of evaluator slugs to run

    def model_dump(self, *args, **kwargs) -> "EvalParamsDict":
        kwargs["exclude_none"] = True
        return super().model_dump(*args, **kwargs)

    @classmethod
    def fix_broken_message(cls, message_obj: dict):
        if not message_obj:
            return {"role": "user", "content": ""}
        elif isinstance(message_obj, Message):
            return message_obj.model_dump()
        elif isinstance(message_obj, dict):
            if "role" not in message_obj:
                message_obj["role"] = "user"
            if "content" not in message_obj:
                message_obj["content"] = ""
        return message_obj

    @field_validator("completion_message", mode="before")
    def validate_completion_message(cls, value):
        return cls.fix_broken_message(value)

    @field_validator("prompt_messages", mode="before")
    def validate_prompt_messages(cls, value):
        if not value:
            return []
        return [cls.fix_broken_message(message) for message in value]


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


class EvalConfigurations(PreprocessEvalConfigurationsMixin, KeywordsAIBaseModel):
    id: str
    organization_id: int
    unique_organization_id: str = ""
    model: Union[str, None] = None
    enabled: bool = False
    sample_percentage: Union[float, None] = None
    eval_class: str
    configurations: BaseEvalFormType
    eval_code_snippet: str = ""
    categorical_choices: Optional[List[dict]] = []
    name: str = ""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.load_configs()

    @classmethod
    def model_validate(cls, *args, **kwargs):
        to_return = super().model_validate(*args, **kwargs)
        to_return.load_configs()
        return to_return

    @field_validator("model")
    def validate_model(cls, value):
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

    model_config = ConfigDict(from_attributes=True)
