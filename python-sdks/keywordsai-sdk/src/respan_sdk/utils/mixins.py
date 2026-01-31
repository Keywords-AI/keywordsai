from pydantic import model_validator

from keywordsai_sdk.constants._internal_constants import (
    RAW_EVAL_CONFIGURATIONS_TO_DB_COLUMN_MAP,
    RAW_EVAL_FORM_TO_DB_COLUMN_MAP,
    RAW_LOG_DATA_TO_DB_COLUMN_MAP,
    RawDataToDBColumnMap,
)


def _map_fields_to_db_column(data: dict, mapping: RawDataToDBColumnMap):
    for key, value in mapping.items():
        if key in data:
            if isinstance(value, str):
                data[value] = data[key]
            elif isinstance(value, dict):
                if value["action"] == "append":
                    data[value["column_name"]] = data[key]
                elif value["action"] == "replace":
                    data[value["column_name"]] = data.pop(key)
    return data


class PreprocessDataMixin:
    """
    A mixin class that provides basic data preprocessing functionality for Pydantic models.
    This mixin map some columns in the raw data to a different column for db storage & the validation of the pydantic model that inherits from it.
    """

    _raw_data_to_db_column_map: RawDataToDBColumnMap = {}

    @classmethod
    def _object_to_dict(self, obj):
        if isinstance(obj, dict):
            return obj
        elif hasattr(obj, "__dict__"):
            return obj.__dict__
        else:
            class_name = (
                self.__class__.__name__
                if hasattr(self.__class__, "__name__")
                else "Unknown"
            )
            raise ValueError(
                f"{class_name} can only be initialized with a dict or an object with a __dict__ attribute"
            )

    @model_validator(mode="before")
    @classmethod
    def _preprocess_data(cls, data):
        if data is None:
            return data
        data = cls._object_to_dict(data)
        data = _map_fields_to_db_column(data, mapping=cls._raw_data_to_db_column_map)
        return data


class PreprocessLogDataMixin(PreprocessDataMixin):
    _raw_data_to_db_column_map: RawDataToDBColumnMap = RAW_LOG_DATA_TO_DB_COLUMN_MAP


class PreprocessEvalFormMixin(PreprocessDataMixin):
    _raw_data_to_db_column_map: RawDataToDBColumnMap = RAW_EVAL_FORM_TO_DB_COLUMN_MAP


class PreprocessEvalConfigurationsMixin(PreprocessDataMixin):
    _raw_data_to_db_column_map: RawDataToDBColumnMap = (
        RAW_EVAL_CONFIGURATIONS_TO_DB_COLUMN_MAP
    )
