from pydantic import model_validator

from keywordsai_sdk.constants._internal_constants import RAW_LOG_DATA_TO_DB_COLUMN_MAP


class PreprocessDataMixin:
    """
    A mixin class that provides basic data preprocessing functionality for Pydantic models.
    This mixin converts objects with __dict__ attribute to dictionaries before validation.
    """

    @model_validator(mode="before")
    @classmethod
    def _preprocess_data(cls, data):
        if isinstance(data, dict):
            pass
        elif hasattr(data, "__dict__"):
            data = data.__dict__
        else:
            class_name = cls.__name__ if hasattr(cls, "__name__") else "Unknown"
            raise ValueError(
                f"{class_name} can only be initialized with a dict or an object with a __dict__ attribute"
            )
        return data


class PreprocessLogDataMixin(PreprocessDataMixin):
    """
    A mixin class that provides log data preprocessing functionality for Pydantic models.
    This mixin converts objects with __dict__ attribute to dictionaries before validation
    and applies field name mappings for log data.
    """

    @model_validator(mode="before")
    @classmethod
    def _preprocess_data(cls, data):
        data = super()._preprocess_data(data)
        
        # Ensure data is not None
        if data is None:
            return data
            
        # Map field names
        for key, value in RAW_LOG_DATA_TO_DB_COLUMN_MAP.items():
            if key in data:
                if isinstance(value, str):
                    data[value] = data[key]
                elif isinstance(value, dict):
                    if value["action"] == "append":
                        data[value["column_name"]] = data[key]
                    elif value["action"] == "replace":
                        data[value["column_name"]] = data.pop(key)
        
        return data
