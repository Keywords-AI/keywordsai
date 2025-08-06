from pydantic import model_validator


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
            class_name = cls.__name__ if hasattr(cls, '__name__') else 'Unknown'
            raise ValueError(
                f"{class_name} can only be initialized with a dict or an object with a __dict__ attribute"
            )
        return data
