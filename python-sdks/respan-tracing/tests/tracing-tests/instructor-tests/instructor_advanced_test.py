"""
Advanced test demonstrating Respan tracing with Instructor's advanced features.

This test showcases:
- Complex nested Pydantic models
- Custom validation with automatic retries
- Error handling and validation failures
- Multiple extraction strategies
- Chain of thought reasoning with structured outputs
"""

from dotenv import load_dotenv
import os
from typing import List, Optional, Literal, Union
from datetime import datetime, date
from pydantic import BaseModel, Field, field_validator, model_validator
from enum import Enum
import instructor
from respan_tracing import RespanTelemetry
from respan_tracing.decorators import task, workflow

# Load environment variables
load_dotenv(".env", override=True)

# Initialize Respan Telemetry
k_tl = RespanTelemetry(app_name="instructor-advanced-test")

# Define advanced Pydantic models with validation
class Priority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class TaskStatus(str, Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    REVIEW = "review"
    DONE = "done"

class Person(BaseModel):
    """A person with validation."""
    name: str = Field(description="Full name of the person")
    email: str = Field(description="Valid email address")
    role: str = Field(description="Job role or title")
    
    @field_validator('email')
    @classmethod
    def validate_email(cls, v):
        if '@' not in v or '.' not in v:
            raise ValueError('Email must contain @ and . characters')
        return v.lower()

class Task(BaseModel):
    """A task with complex validation."""
    title: str = Field(description="Task title", min_length=5, max_length=100)
    description: str = Field(description="Detailed task description")
    priority: Priority = Field(description="Task priority level")
    status: TaskStatus = Field(description="Current task status")
    assignee: Person = Field(description="Person assigned to this task")
    estimated_hours: float = Field(description="Estimated hours to complete", ge=0.5, le=100)
    due_date: str = Field(description="Due date in YYYY-MM-DD format")
    tags: List[str] = Field(description="List of relevant tags", min_length=1, max_length=5)
    
    @field_validator('due_date')
    @classmethod
    def validate_due_date(cls, v):
        try:
            # Parse the date to ensure it's valid
            parsed_date = datetime.strptime(v, '%Y-%m-%d').date()
            # Ensure it's not in the past
            if parsed_date < date.today():
                raise ValueError('Due date cannot be in the past')
            return v
        except ValueError as e:
            if "time data" in str(e):
                raise ValueError('Due date must be in YYYY-MM-DD format')
            raise e

class ProjectSummary(BaseModel):
    """Project summary with nested validation."""
    project_name: str = Field(description="Name of the project")
    description: str = Field(description="Project description")
    total_tasks: int = Field(description="Total number of tasks", ge=1)
    completed_tasks: int = Field(description="Number of completed tasks", ge=0)
    team_members: List[Person] = Field(description="List of team members", min_length=1)
    high_priority_tasks: List[Task] = Field(description="List of high priority tasks")
    estimated_completion_date: str = Field(description="Estimated project completion date")
    
    @model_validator(mode='after')
    def validate_task_counts(self):
        if self.completed_tasks > self.total_tasks:
            raise ValueError('Completed tasks cannot exceed total tasks')
        return self

class ReasoningStep(BaseModel):
    """A step in chain of thought reasoning."""
    step_number: int = Field(description="Step number in the reasoning process")
    description: str = Field(description="Description of this reasoning step")
    conclusion: str = Field(description="Conclusion or insight from this step")

class ChainOfThoughtAnalysis(BaseModel):
    """Chain of thought analysis with reasoning steps."""
    question: str = Field(description="The original question being analyzed")
    reasoning_steps: List[ReasoningStep] = Field(description="List of reasoning steps", min_length=3)
    final_answer: str = Field(description="Final answer based on reasoning")
    confidence_score: float = Field(description="Confidence in the answer (0-1)", ge=0, le=1)

# Initialize Instructor client
client = instructor.from_provider("openai/gpt-4o-mini")

@task(name="extract_complex_task")
def extract_task_with_validation(text: str) -> Task:
    """Extract a task with complex validation and automatic retries."""
    try:
        task = client.chat.completions.create(
            response_model=Task,
            messages=[
                {"role": "system", "content": """
                Extract task information from the provided text. 
                Ensure all validation requirements are met:
                - Title must be 5-100 characters
                - Email must contain @ and .
                - Estimated hours must be between 0.5 and 100
                - Due date must be in YYYY-MM-DD format and not in the past
                - Include 1-5 relevant tags
                """},
                {"role": "user", "content": text}
            ],
            temperature=0.1,
            max_tokens=800,
            max_retries=3  # Instructor will retry on validation failures
        )
        return task
    except Exception as e:
        print(f"❌ Task extraction failed: {e}")
        raise

@task(name="extract_project_summary")
def extract_project_summary(text: str) -> ProjectSummary:
    """Extract a complex project summary with nested models."""
    try:
        project = client.chat.completions.create(
            response_model=ProjectSummary,
            messages=[
                {"role": "system", "content": """
                Extract comprehensive project information from the text.
                Create realistic team member profiles with valid emails.
                Ensure completed tasks don't exceed total tasks.
                Generate high priority tasks that are relevant to the project.
                """},
                {"role": "user", "content": text}
            ],
            temperature=0.2,
            max_tokens=1500,
            max_retries=3
        )
        return project
    except Exception as e:
        print(f"❌ Project extraction failed: {e}")
        raise

@task(name="chain_of_thought_analysis")
def perform_chain_of_thought_analysis(question: str) -> ChainOfThoughtAnalysis:
    """Perform chain of thought reasoning with structured output."""
    analysis = client.chat.completions.create(
        response_model=ChainOfThoughtAnalysis,
        messages=[
            {"role": "system", "content": """
            Analyze the given question using chain of thought reasoning.
            Break down your thinking into clear, logical steps.
            Provide at least 3 reasoning steps.
            Give a confidence score for your final answer.
            """},
            {"role": "user", "content": question}
        ],
        temperature=0.3,
        max_tokens=1000
    )
    return analysis

@task(name="test_validation_failures")
def test_validation_with_bad_data():
    """Test how Instructor handles validation failures with retries."""
    bad_task_text = """
    Task: Fix
    Description: Fix the bug
    Assignee: John (invalid-email)
    Priority: super-high
    Due: yesterday
    Hours: -5
    """
    
    print("🧪 Testing validation with intentionally bad data...")
    try:
        # This should fail validation and trigger retries
        task = extract_task_with_validation(bad_task_text)
        print(f"✅ Surprisingly succeeded: {task}")
        return task
    except Exception as e:
        print(f"❌ Expected validation failure: {e}")
        return None

@workflow(name="advanced_structured_extraction")
def run_advanced_extraction_tests():
    """Run advanced structured extraction tests."""
    
    # Test 1: Complex task extraction with validation
    print("\n=== Test 1: Complex Task Extraction ===")
    task_text = """
    We need to implement a new user authentication system for our web application.
    This is a high priority task that should be assigned to Sarah Johnson (sarah.johnson@techcorp.com),
    our senior backend developer. The task should take approximately 15 hours to complete
    and needs to be finished by 2025-01-15. This involves security, backend development,
    database design, API integration, and testing.
    """
    
    task = extract_task_with_validation(task_text)
    print(f"✅ Extracted Task: {task.title}")
    print(f"   Assignee: {task.assignee.name} ({task.assignee.email})")
    print(f"   Priority: {task.priority}, Status: {task.status}")
    print(f"   Due: {task.due_date}, Hours: {task.estimated_hours}")
    print(f"   Tags: {', '.join(task.tags)}")
    
    # Test 2: Complex project summary
    print("\n=== Test 2: Project Summary Extraction ===")
    project_text = """
    The E-commerce Platform Modernization project is a comprehensive initiative to upgrade
    our legacy online shopping system. The project involves 25 total tasks, with 8 already
    completed. Our team consists of:
    - Alice Chen (alice.chen@company.com) - Project Manager
    - Bob Martinez (bob.martinez@company.com) - Lead Developer  
    - Carol Kim (carol.kim@company.com) - UI/UX Designer
    - David Singh (david.singh@company.com) - QA Engineer
    
    High priority tasks include:
    1. Database migration (assigned to Bob, 20 hours, due 2025-01-20)
    2. Payment gateway integration (assigned to Alice, 12 hours, due 2025-01-25)
    3. Security audit (assigned to David, 8 hours, due 2025-01-30)
    
    We expect to complete the entire project by 2025-02-15.
    """
    
    project = extract_project_summary(project_text)
    print(f"✅ Project: {project.project_name}")
    print(f"   Progress: {project.completed_tasks}/{project.total_tasks} tasks")
    print(f"   Team: {len(project.team_members)} members")
    print(f"   High Priority Tasks: {len(project.high_priority_tasks)}")
    print(f"   Completion: {project.estimated_completion_date}")
    
    # Test 3: Chain of thought reasoning
    print("\n=== Test 3: Chain of Thought Analysis ===")
    question = """
    A software development team has 5 developers. Each developer can complete 2 features per week.
    The project requires 30 features total. However, 20% of features typically need rework due to
    changing requirements. How long will the project take to complete?
    """
    
    analysis = perform_chain_of_thought_analysis(question)
    print(f"✅ Question: {analysis.question}")
    print(f"   Reasoning Steps: {len(analysis.reasoning_steps)}")
    for step in analysis.reasoning_steps:
        print(f"   Step {step.step_number}: {step.description}")
    print(f"   Final Answer: {analysis.final_answer}")
    print(f"   Confidence: {analysis.confidence_score:.2f}")
    
    # Test 4: Validation failure handling
    print("\n=== Test 4: Validation Failure Handling ===")
    validation_result = test_validation_failures()
    
    return {
        "task": task,
        "project": project,
        "analysis": analysis,
        "validation_test": validation_result
    }

@task(name="validate_advanced_results")
def validate_advanced_results(results: dict):
    """Validate the advanced extraction results."""
    
    # Validate task
    task = results["task"]
    assert task.priority in [p.value for p in Priority], f"Invalid priority: {task.priority}"
    assert '@' in task.assignee.email, f"Invalid email: {task.assignee.email}"
    assert task.estimated_hours >= 0.5, f"Invalid hours: {task.estimated_hours}"
    assert len(task.tags) >= 1, f"No tags found: {task.tags}"
    
    # Validate project
    project = results["project"]
    assert project.completed_tasks <= project.total_tasks, "Completed > total tasks"
    assert len(project.team_members) >= 1, "No team members found"
    assert len(project.high_priority_tasks) >= 1, "No high priority tasks found"
    
    # Validate analysis
    analysis = results["analysis"]
    assert len(analysis.reasoning_steps) >= 3, f"Not enough reasoning steps: {len(analysis.reasoning_steps)}"
    assert 0 <= analysis.confidence_score <= 1, f"Invalid confidence: {analysis.confidence_score}"
    
    print("✅ All advanced validation checks passed!")
    return True

@workflow(name="instructor_advanced_demo")
def main():
    """Main workflow for advanced Instructor features with Respan tracing."""
    print("🚀 Starting Advanced Instructor + Respan Tracing Demo")
    print("=" * 60)
    
    # Run advanced extraction tests
    results = run_advanced_extraction_tests()
    
    # Validate results
    validation_passed = validate_advanced_results(results)
    
    print("\n" + "=" * 60)
    print("✅ Advanced demo completed successfully!")
    print(f"✅ Validation passed: {validation_passed}")
    print("\n📊 Advanced features demonstrated:")
    print("   ✅ Complex nested Pydantic models")
    print("   ✅ Custom validation with automatic retries")
    print("   ✅ Chain of thought reasoning")
    print("   ✅ Error handling and validation failures")
    print("   ✅ Multiple extraction strategies")
    print("\n📈 Check your Respan dashboard for detailed traces:")
    print("   - Retry attempts on validation failures")
    print("   - Complex model validation traces")
    print("   - Chain of thought reasoning steps")
    print("   - Token usage for advanced prompts")
    
    return results

if __name__ == "__main__":
    main()