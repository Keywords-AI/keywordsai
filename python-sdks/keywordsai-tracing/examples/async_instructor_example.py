"""
Simple Async Instructor + KeywordsAI Tracing Example

This example shows how easy it is to add KeywordsAI tracing to your async Instructor workflows.
Just 3 lines of setup, then your structured outputs are automatically traced!
"""

import asyncio
import os
from pydantic import BaseModel, Field
import instructor
from openai import AsyncOpenAI
from keywordsai_tracing import KeywordsAITelemetry, Instruments
from keywordsai_tracing.decorators import task
from dotenv import load_dotenv
load_dotenv()

# 1️⃣ Initialize KeywordsAI tracing (one line!)
k_tl = KeywordsAITelemetry(app_name="async-instructor-demo", instruments={Instruments.OPENAI})

# 2️⃣ Set up your async Instructor client (your existing code)
async_client = AsyncOpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
instructor_client = instructor.from_openai(async_client)

# 3️⃣ Define your Pydantic models (your existing code)
class User(BaseModel):
    name: str = Field(description="Full name")
    age: int = Field(description="Age in years")
    email: str = Field(description="Email address")
    role: str = Field(description="Job title")

# 4️⃣ Add @task decorator to your functions (one line per function!)
@task(name="extract_user_async")
async def extract_user(text: str) -> User:
    """Extract user information using async Instructor."""
    return await instructor_client.chat.completions.create(
        model="gpt-4o-mini",
        response_model=User,
        messages=[
            {"role": "system", "content": "Extract user information from the text."},
            {"role": "user", "content": text}
        ],
        temperature=0.1
    )

async def main():
    """Demo the async extraction with tracing."""
    
    # Sample text
    user_text = """
    Meet Alex Johnson, a 32-year-old Senior Software Engineer at Google.
    You can reach Alex at alex.johnson@google.com for any technical questions.
    """
    
    # Extract user (automatically traced!)
    user = await extract_user(user_text)
    
    print(user.model_dump())

if __name__ == "__main__":
    asyncio.run(main())