from keywordsai_sdk.utils.conversion import anthropic_params_to_llm_params
from keywordsai_sdk.keywordsai_types._internal_types import AnthropicParams
raw_params = {
    "model": "claude-3-5-sonnet-20241022",
    "messages": [
        {"role": "user", "content": "What is the capital of France?"}
    ],
    "tools": [
        {
            "type": "computer_20241022",
            "name": "compute_tool",
            "description": "Compute the capital of France",
            "display_height_px": 100,
            "display_width_px": 100,
            "display_number": 1,
        }
    ]
}

anthropic_params = AnthropicParams(**raw_params)

llm_params = anthropic_params_to_llm_params(anthropic_params)

import json
print(json.dumps(llm_params.model_dump(exclude_none=True), indent=4))