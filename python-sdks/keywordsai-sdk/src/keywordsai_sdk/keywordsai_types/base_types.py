from pydantic import BaseModel

class KeywordsAIBaseModel(BaseModel):
    def __contains__(self, key):
        # Define custom behavior for the 'in' operator
        return hasattr(self, key)

    def get(self, key, default=None):
        # Custom .get() method to access attributes with a default value if the attribute doesn't exist
        return getattr(self, key, default)

    def __getitem__(self, key):
        # Allow dictionary-style access to attributes
        return getattr(self, key)

    def __setitem__(self, key, value):
        # Allow dictionary-style assignment to attributes
        setattr(self, key, value)

    def _assign_related_field(
        self, related_model_name: str, assign_to_name: str, data: dict
    ):
        related_model_value = data.get(related_model_name)
        if not isinstance(related_model_value, (int, str)):
            return
        data[assign_to_name] = related_model_value
