from typing import List, Optional, Union
from keywordsai_sdk.keywordsai_types.base_types import KeywordsAIBaseModel

class CustomSpelling(KeywordsAIBaseModel):
    from_words: List[str]
    to: str

class AssemblyAIParams(KeywordsAIBaseModel):
    api_key: str
    audio_url: str
    audio_end_at: Optional[int] = None
    audio_start_from: Optional[int] = None
    auto_chapters: Optional[bool] = False
    auto_highlights: Optional[bool] = False
    boost_param: Optional[str] = None  # "low", "default", "high"
    content_safety: Optional[bool] = False
    content_safety_confidence: Optional[int] = 50
    custom_spelling: Optional[List[CustomSpelling]] = None
    disfluencies: Optional[bool] = False
    entity_detection: Optional[bool] = False
    filter_profanity: Optional[bool] = False
    format_text: Optional[bool] = True
    iab_categories: Optional[bool] = False
    language_code: Optional[str] = "en_us"
    language_confidence_threshold: Optional[float] = 0.0
    language_detection: Optional[bool] = False
    multichannel: Optional[bool] = False
    punctuate: Optional[bool] = True
    redact_pii: Optional[bool] = False
    redact_pii_audio: Optional[bool] = False
    redact_pii_audio_quality: Optional[str] = "mp3"  # "mp3" or "wav"
    redact_pii_policies: Optional[List[str]] = None
    redact_pii_sub: Optional[str] = None  # "entity_name" or "hash"
    sentiment_analysis: Optional[bool] = False
    speaker_labels: Optional[bool] = False
    speakers_expected: Optional[int] = None
    speech_model: Optional[str] = None  # "best" or "nano"
    speech_threshold: Optional[float] = None
    summarization: Optional[bool] = False
    summary_model: Optional[str] = None  # "informative", "conversational", "catchy"
    summary_type: Optional[str] = None  # "bullets", "bullets_verbose", "gist", "headline", "paragraph"
    topics: Optional[List[str]] = None
    webhook_auth_header_name: Optional[str] = None
    webhook_auth_header_value: Optional[str] = None
    webhook_url: Optional[str] = None
    word_boost: Optional[List[str]] = None
    custom_topics: Optional[bool] = False
    dual_channel: Optional[bool] = False
    