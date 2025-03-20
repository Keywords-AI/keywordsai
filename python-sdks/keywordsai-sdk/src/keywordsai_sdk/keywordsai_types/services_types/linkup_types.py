from typing import Optional, List, Literal, Dict, Any
from pydantic import Field, ConfigDict
from keywordsai_sdk.keywordsai_types.base_types import KeywordsAIBaseModel


class LinkupParams(KeywordsAIBaseModel):
    """
    Parameters for the Linkup API search endpoint.
    
    Based on the Linkup API documentation: https://docs.linkup.so/pages/documentation/api-reference/endpoint/post-search
    """
    apiKey:str
    q: str = Field(..., description="The search query")
    depth: Optional[Literal["standard", "deep"]] = Field(
        None, 
        description="The depth of the search. 'shallow' for faster results, 'deep' for more comprehensive results"
    )
    outputType: Optional[Literal["sourcedAnswer", "structured", "searchResults"]] = Field(
        None, 
        description="The type of output. 'sourcedAnswer' for an answer with sources, 'raw' for raw search results"
    )
    structuredOutputSchema: Optional[str] = Field(
        None, 
        description="JSON schema for structured output"
    )
    includeImages: Optional[bool] = Field(
        None, 
        description="Whether to include images in the response"
    )
    fromDate: Optional[str] = Field(
        None,
        description="The start date for the search in YYYY-MM-DD format"
    )
    toDate: Optional[str] = Field(
        None,
        description="The end date for the search in YYYY-MM-DD format"
    )
    mockResponse: Optional[dict] = None
    def model_dump(self, *args, **kwargs) -> Dict[str, Any]:
        kwargs["exclude_none"] = True
        return super().model_dump(*args, **kwargs)


class LinkupSource(KeywordsAIBaseModel):
    """
    Represents a source in the Linkup API response.
    """
    name: str
    url: str
    snippet: str


class LinkupResponse(KeywordsAIBaseModel):
    """
    Response from the Linkup API search endpoint.
    """
    answer: str
    sources: List[LinkupSource]
