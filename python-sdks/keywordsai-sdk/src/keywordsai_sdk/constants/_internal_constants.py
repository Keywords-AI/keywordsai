from typing import Literal, Dict, Union
from typing_extensions import TypedDict

LogDataToDBColumnAction = Literal["append", "replace"]


class DBColumnToMapToAction(TypedDict):
    column_name: str
    action: LogDataToDBColumnAction


RawDataToDBColumnMap = Dict[str, Union[str, DBColumnToMapToAction]]


RAW_LOG_DATA_TO_DB_COLUMN_MAP: RawDataToDBColumnMap = {
    "ttft": "time_to_first_token",  # Map ttft (in docs) to time_to_first_token column in db
    "generation_time": "latency",  # Map generation_time (in docs) to latency column in db
    # 2025-06-12: trace_group and threads are going to be merged into trace sessions
    "thread_identifier": "session_identifier",
    "trace_group_identifier": "session_identifier",  # This has higher priority than threads in defining session id, placed later than thread_identifier for overriding
    "messages": {
        "column_name": "prompt_messages",
        "action": "append",
    },
}


RAW_EVAL_FORM_TO_DB_COLUMN_MAP: RawDataToDBColumnMap = {
    "conditions": "passing_conditions",  # As of 2025-08-07, deprecated conditions to use centralized passing_condition based on MetricFilterParamPydantic
}

RAW_EVAL_CONFIGURATIONS_TO_DB_COLUMN_MAP: RawDataToDBColumnMap = {
    "human_annotation_choices": "categorical_choices",
}