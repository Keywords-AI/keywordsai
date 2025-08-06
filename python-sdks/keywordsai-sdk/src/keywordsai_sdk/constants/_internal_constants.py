from typing import Literal, Dict, Union
from typing_extensions import TypedDict

LogDataToDBColumnAction = Literal["append", "replace"]


class DBColumnToMapToAction(TypedDict):
    column_name: str
    action: LogDataToDBColumnAction


LogDataToDBColumnMap = Dict[str, Union[str, DBColumnToMapToAction]]


RAW_LOG_DATA_TO_DB_COLUMN_MAP: LogDataToDBColumnMap = {
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
