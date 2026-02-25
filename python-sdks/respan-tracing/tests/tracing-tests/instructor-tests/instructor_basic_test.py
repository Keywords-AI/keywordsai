"""
Basic test demonstrating Respan tracing with Instructor structured outputs.

This test shows how Respan tracing automatically captures:
- LLM requests and responses through Instructor
- Structured output validation and parsing
- Token usage and costs
- Model parameters and settings
"""

from dotenv import load_dotenv
import os
from typing import List, Optional
from pydantic import BaseModel, Field
import instructor
from respan_tracing import RespanTelemetry
from respan_tracing.decorators import task, workflow

# Load environment variables
load_dotenv(".env", override=True)

# Initialize Respan Telemetry
print("RESPAN_BASE_URL:", os.environ.get("RESPAN_BASE_URL"))
print("RESPAN_API_KEY:", os.environ.get("RESPAN_API_KEY"))
k_tl = RespanTelemetry(app_name="instructor-basic-test")

# Define Pydantic models for structured outputs
class User(BaseModel):
    """A user with basic information."""
    name: str = Field(description="The user's full name")
    age: int = Field(description="The user's age in years", ge=0, le=150)
    email: Optional[str] = Field(description="The user's email address", default=None)
    occupation: Optional[str] = Field(description="The user's job or profession", default=None)

class CompanyInfo(BaseModel):
    """Information about a company."""
    name: str = Field(description="Company name")
    industry: str = Field(description="Industry or sector")
    employees: int = Field(description="Number of employees", ge=1)
    founded_year: int = Field(description="Year the company was founded", ge=1800, le=2024)
    headquarters: str = Field(description="Location of headquarters")

class UserList(BaseModel):
    """A list of users with metadata."""
    users: List[User] = Field(description="List of users")
    total_count: int = Field(description="Total number of users")
    source: str = Field(description="Source of the user data")

# Initialize Instructor client with OpenAI
client = instructor.from_provider("openai/gpt-4o-mini")

@task(name="extract_single_user")
def extract_user_info(text: str) -> User:
    """Extract user information from text using structured output."""
    user = client.chat.completions.create(
        response_model=User,
        messages=[
            {"role": "system", "content": "Extract user information from the provided text."},
            {"role": "user", "content": text}
        ],
        temperature=0.1,
        max_tokens=500
    )
    return user

@task(name="extract_company_info")
def extract_company_info(text: str) -> CompanyInfo:
    """Extract company information from text using structured output."""
    company = client.chat.completions.create(
        response_model=CompanyInfo,
        messages=[
            {"role": "system", "content": "Extract company information from the provided text. Make reasonable estimates for missing information."},
            {"role": "user", "content": text}
        ],
        temperature=0.1,
        max_tokens=500
    )
    return company

@task(name="extract_multiple_users")
def extract_user_list(text: str) -> UserList:
    """Extract multiple users from text using structured output."""
    user_list = client.chat.completions.create(
        response_model=UserList,
        messages=[
            {"role": "system", "content": "Extract all user information from the provided text and organize it into a structured list."},
            {"role": "user", "content": text}
        ],
        temperature=0.1,
        max_tokens=1000
    )
    return user_list

@workflow(name="structured_data_extraction_workflow")
def run_structured_extraction_tests():
    """Run various structured data extraction tests with Instructor."""
    
    # Test 1: Single user extraction
    print("\n=== Test 1: Single User Extraction ===")
    user_text = """
    John Smith is a 32-year-old software engineer working at Google. 
    His email is john.smith@gmail.com and he specializes in machine learning.
    """
    
    user = extract_user_info(user_text)
    print(f"Extracted User: {user}")
    
    # Test 2: Company information extraction
    print("\n=== Test 2: Company Information Extraction ===")
    company_text = """
    TechCorp is a leading technology company founded in 2010. 
    They specialize in artificial intelligence and machine learning solutions.
    The company is headquartered in San Francisco, California and has approximately 500 employees.
    """
    
    company = extract_company_info(company_text)
    print(f"Extracted Company: {company}")
    
    # Test 3: Multiple users extraction
    print("\n=== Test 3: Multiple Users Extraction ===")
    users_text = """
    Our team consists of several talented individuals:
    - Alice Johnson, 28, is our lead designer with alice@company.com
    - Bob Wilson, 35, works as a product manager 
    - Carol Davis, 42, is our senior developer specializing in backend systems
    - David Brown, 29, is our marketing specialist with david.brown@company.com
    
    This information comes from our employee directory.
    """
    
    user_list = extract_user_list(users_text)
    print(f"Extracted User List: {user_list}")
    print(f"Total users found: {user_list.total_count}")
    
    return {
        "single_user": user,
        "company": company,
        "user_list": user_list
    }

@task(name="validate_extraction_results")
def validate_results(results: dict):
    """Validate that the extraction results meet our expectations."""
    
    # Validate single user
    user = results["single_user"]
    assert user.name == "John Smith", f"Expected 'John Smith', got '{user.name}'"
    assert user.age == 32, f"Expected age 32, got {user.age}"
    assert user.email == "john.smith@gmail.com", f"Expected 'john.smith@gmail.com', got '{user.email}'"
    
    # Validate company
    company = results["company"]
    assert company.name == "TechCorp", f"Expected 'TechCorp', got '{company.name}'"
    assert company.founded_year == 2010, f"Expected 2010, got {company.founded_year}"
    assert company.employees == 500, f"Expected 500 employees, got {company.employees}"
    
    # Validate user list
    user_list = results["user_list"]
    assert user_list.total_count >= 4, f"Expected at least 4 users, got {user_list.total_count}"
    assert len(user_list.users) >= 4, f"Expected at least 4 users in list, got {len(user_list.users)}"
    
    print("✅ All validation checks passed!")
    return True

@workflow(name="instructor_basic_demo")
def main():
    """Main workflow demonstrating Instructor with Respan tracing."""
    print("🚀 Starting Instructor + Respan Tracing Demo")
    print("=" * 50)
    
    # Run the extraction tests
    results = run_structured_extraction_tests()
    
    # Validate the results
    validation_passed = validate_results(results)
    
    print("\n" + "=" * 50)
    print("✅ Demo completed successfully!")
    print(f"✅ Validation passed: {validation_passed}")
    print("\n📊 Check your Respan dashboard to see the traced LLM calls:")
    print("   - Structured output requests and responses")
    print("   - Token usage and costs")
    print("   - Model parameters and validation")
    print("   - Workflow execution traces")
    
    return results

if __name__ == "__main__":
    main()