"""
Test the new public log types to ensure they work correctly with LLM parameter mapping.
"""
import pytest
from keywordsai_sdk.keywordsai_types.log_types import KeywordsAILogParams, KeywordsAITextLogParams
from keywordsai_sdk.utils.pre_processing import validate_and_separate_log_and_llm_params


def test_keywordsai_log_params_basic():
    """Test basic KeywordsAILogParams functionality."""
    params = {
        "custom_identifier": "test_123",
        "environment": "test",
        "metadata": {"key": "value"},
        "cache_enabled": True,
    }
    
    log_params = KeywordsAILogParams(**params)
    assert log_params.custom_identifier == "test_123"
    assert log_params.environment == "test"
    assert log_params.metadata == {"key": "value"}
    assert log_params.cache_enabled is True


def test_messages_to_prompt_messages_mapping():
    """Test that 'messages' gets mapped to 'prompt_messages' in preprocessing."""
    messages = [
        {"role": "user", "content": "Hello"},
        {"role": "assistant", "content": "Hi there!"}
    ]
    
    params = {
        "messages": messages,
        "custom_identifier": "test_mapping",
    }
    
    log_params = KeywordsAILogParams(**params)
    
    # The _preprocess_data_for_public method should map messages -> prompt_messages
    assert log_params.prompt_messages == messages
    

def test_keywordsai_text_log_params():
    """Test KeywordsAITextLogParams which combines public log params with LLM params."""
    params = {
        "model": "gpt-3.5-turbo",
        "messages": [{"role": "user", "content": "Hello"}],
        "temperature": 0.7,
        "custom_identifier": "test_text_log",
        "environment": "production",
    }
    
    text_log_params = KeywordsAITextLogParams(**params)
    assert text_log_params.model == "gpt-3.5-turbo"
    assert text_log_params.temperature == 0.7
    assert text_log_params.custom_identifier == "test_text_log"
    assert text_log_params.environment == "production"


def test_validate_and_separate_public_params():
    """Test the new public validation function."""
    params = {
        "model": "gpt-4",
        "messages": [{"role": "user", "content": "Test"}],
        "temperature": 0.5,
        "custom_identifier": "validation_test",
        "metadata": {"test": True},
    }
    
    llm_params, log_params = validate_and_separate_log_and_llm_params(params)
    
    # Check LLM params
    assert llm_params.model == "gpt-4"
    assert llm_params.temperature == 0.5
    
    # Check log params
    assert log_params.custom_identifier == "validation_test"
    assert log_params.metadata == {"test": True}
    assert log_params.prompt_messages == [{"role": "user", "content": "Test"}]


def test_public_vs_internal_separation():
    """Test that public log params only contain user-facing fields."""
    # These fields should be available in public params
    public_fields = [
        "custom_identifier", "environment", "metadata", "cache_enabled",
        "prompt_messages", "trace_unique_id", "session_identifier"
    ]
    
    # These fields should NOT be available in public params (internal only)
    internal_only_fields = [
        "error_bit", "storage_object_key", "is_fts_enabled", 
        "cache_hit", "cache_bit", "prompt_message_count"
    ]
    
    log_params_fields = set(KeywordsAILogParams.__annotations__.keys())
    
    # Check that public fields are present
    for field in public_fields:
        assert field in log_params_fields, f"Public field '{field}' missing from KeywordsAILogParams"
    
    # Check that internal-only fields are NOT present
    for field in internal_only_fields:
        assert field not in log_params_fields, f"Internal field '{field}' should not be in KeywordsAILogParams"


if __name__ == "__main__":
    pytest.main([__file__])