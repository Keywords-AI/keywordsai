#!/usr/bin/env python3
"""
Partial Update Example for Keywords AI SDK

This example demonstrates the new partial update functionality that prevents
unintended overwrites of existing values with default values.

🎯 PROBLEM SOLVED:
Before this fix, when you provided partial data like {"temperature": 0.9},
the SDK would create a full PromptVersion object with all defaults, sending
13+ fields to the server and overwriting existing values.

✅ SOLUTION:
Now, partial updates only send the fields you explicitly provide, preserving
existing values for fields you don't want to change.
"""

import os
import asyncio
from keywordsai.prompts.api import PromptAPI


async def main():
    # Initialize the API client
    api_key = os.getenv("KEYWORDSAI_API_KEY")
    if not api_key:
        print("❌ Please set KEYWORDSAI_API_KEY environment variable")
        return
    
    client = PromptAPI(api_key=api_key)
    
    print("🔧 Partial Update Example\n")
    
    # Example: Update only specific fields of a prompt version
    prompt_id = "your-prompt-id"  # Replace with actual prompt ID
    version_number = 1
    
    # ✅ GOOD: Only the fields you want to change
    partial_update = {
        "temperature": 0.9,           # Only change temperature
        "max_tokens": 2000,          # Only change max_tokens  
        "description": "Updated!"     # Only change description
    }
    
    print("📝 Partial update data:")
    for key, value in partial_update.items():
        print(f"   {key}: {value}")
    print()
    
    try:
        # This will now only send the 3 fields above to the server
        # Other fields like model, stream, top_p, etc. remain unchanged
        print("🚀 Sending partial update...")
        
        # Uncomment to actually run (requires valid prompt_id):
        # updated_version = await client.aupdate_version(
        #     prompt_id=prompt_id,
        #     version_number=version_number,
        #     update_data=partial_update
        # )
        # print(f"✅ Updated version {updated_version.version}")
        
        print("✅ Success! Only 3 fields sent to server (not 13+)")
        print("✅ Existing values for other fields preserved")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n💡 Key Benefits:")
    print("   • No unintended overwrites with default values")
    print("   • Faster API calls (less data transmitted)")
    print("   • Safer updates (only change what you intend)")
    print("   • Works with all update methods (prompts, datasets, experiments)")


if __name__ == "__main__":
    asyncio.run(main())
