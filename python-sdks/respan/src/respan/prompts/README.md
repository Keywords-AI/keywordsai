# Prompt API

The Prompt API provides functionality for managing prompts and their versions in Keywords AI.

## Quick Start

```python
from respan import PromptAPI
from respan_sdk.respan_types.prompt_types import Prompt, PromptVersion

# Initialize client
client = PromptAPI(api_key="your-api-key")

# Create a prompt
prompt = client.create()

# Create a version
version = client.create_version(prompt.id, PromptVersion(
    prompt_version_id="v1",
    messages=[{"role": "system", "content": "You are helpful."}],
    model="gpt-4o-mini"
))
```

## Available Methods

### Prompt Management
- `create()` - Create a new prompt
- `list(page, page_size, **filters)` - List prompts with pagination
- `get(resource_id)` - Retrieve a specific prompt
- `update(resource_id, update_data)` - Update prompt properties
- `delete(resource_id)` - Delete a prompt

### Version Management
- `create_version(prompt_id, version_data)` - Create a new version
- `list_versions(prompt_id, page, page_size, **filters)` - List versions for a prompt
- `get_version(prompt_id, version_number)` - Retrieve a specific version
- `update_version(prompt_id, version_number, update_data)` - Update version properties

## Async Support

All methods have async variants with the `a` prefix:

```python
import asyncio

async def main():
    client = PromptAPI(api_key="your-api-key")
    
    # Async operations
    prompt = await client.acreate()
    prompts = await client.alist()
    version = await client.acreate_version(prompt.id, version_data)

asyncio.run(main())
```

## Key Features

- **Prompt Management** - Create and organize prompts
- **Version Control** - Manage different versions of prompts with specific configurations
- **Template Support** - Use message templates with variables
- **Model Configuration** - Set model parameters like temperature, max_tokens, etc.
- **Sync/Async** - Both synchronous and asynchronous operations supported
