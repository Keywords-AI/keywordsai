from datetime import datetime
from typing import Union


def parse_datetime(v: Union[str, datetime]) -> datetime:
    if isinstance(v, str):
        # Lazy import to improve import speed
        from dateparser import parse

        try:
            value = datetime.fromisoformat(v)
            return value
        except Exception as e:
            try:
                value = parse(v)
                return value
            except Exception as e:
                raise ValueError(
                    "timestamp has to be a valid ISO 8601 formatted date-string YYYY-MM-DD"
                )
    return v