#!/usr/bin/env python3
"""
Experiment API Real Integration Tests

These tests use real API calls to validate experiment functionality.
No mocking - tests actual SDK behavior with Keywords AI server.

Environment variables required:
- KEYWORDSAI_API_KEY
- KEYWORDSAI_BASE_URL

Usage:
    python -m pytest tests/test_experiment_api_real.py -v -s
"""

import pytest
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv(override=True)

from keywordsai.experiments.api import ExperimentAPI
from keywordsai.types.experiment_types import (
    ExperimentCreate,
    ExperimentColumnType,
    ExperimentRowType,
    AddExperimentRowsRequest,
    RemoveExperimentRowsRequest,
    UpdateExperimentRowsRequest,
    AddExperimentColumnsRequest,
    RemoveExperimentColumnsRequest,
    UpdateExperimentColumnsRequest,
    RunExperimentRequest,
    RunExperimentEvalsRequest,
)


@pytest.fixture
def api_key():
    """Get API key from environment"""
    key = os.getenv("KEYWORDSAI_API_KEY")
    if not key:
        pytest.skip("KEYWORDSAI_API_KEY not found in environment")
    return key


@pytest.fixture
def base_url():
    """Get base URL from environment"""
    return os.getenv("KEYWORDSAI_BASE_URL", "http://localhost:8000")


@pytest.fixture
def experiment_api(api_key, base_url):
    """Experiment API client"""
    return ExperimentAPI(api_key=api_key, base_url=base_url)


@pytest.fixture
def test_column():
    """Sample experiment column for testing"""
    return ExperimentColumnType(
        model="gpt-3.5-turbo",
        name="SDK Test Column",
        temperature=0.7,
        max_completion_tokens=256,
        top_p=1.0,
        frequency_penalty=0.0,
        presence_penalty=0.0,
        prompt_messages=[
            {
                "role": "system",
                "content": "You are a helpful assistant for SDK testing."
            },
            {
                "role": "user", 
                "content": "{{user_input}}"
            }
        ],
        tools=[],
        tool_choice="auto",
        response_format={"type": "text"}
    )


@pytest.fixture
def test_row():
    """Sample experiment row for testing"""
    return ExperimentRowType(
        input={"user_input": "What is 2+2?"},
        ideal_output="4"
    )


class TestExperimentAPICRUD:
    """Test basic CRUD operations for experiments"""
    
    def test_create_experiment_sync(self, experiment_api, test_column, test_row):
        """Test creating an experiment synchronously"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        experiment_data = ExperimentCreate(
            name=f"SDK_TEST_Experiment_{timestamp}",
            description="Integration test experiment created by SDK",
            columns=[test_column],
            rows=[test_row]
        )
        
        # Create experiment
        experiment = experiment_api.create(experiment_data)
        
        # Validate response
        assert experiment.id is not None
        assert experiment.name == experiment_data.name
        assert experiment.description == experiment_data.description
        assert len(experiment.columns) == 1
        assert len(experiment.rows) == 1
        
        # Store for cleanup
        self.created_experiment_id = experiment.id
        
        # Clean up
        experiment_api.delete(experiment.id)

    @pytest.mark.asyncio
    async def test_create_experiment_async(self, experiment_api, test_column, test_row):
        """Test creating an experiment asynchronously"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        experiment_data = ExperimentCreate(
            name=f"SDK_TEST_Async_Experiment_{timestamp}",
            description="Async integration test experiment created by SDK",
            columns=[test_column],
            rows=[test_row]
        )
        
        # Create experiment
        experiment = await experiment_api.acreate(experiment_data)
        
        # Validate response
        assert experiment.id is not None
        assert experiment.name == experiment_data.name
        assert experiment.description == experiment_data.description
        assert len(experiment.columns) == 1
        assert len(experiment.rows) == 1
        
        # Clean up
        await experiment_api.adelete(experiment.id)

    def test_list_experiments_sync(self, experiment_api):
        """Test listing experiments synchronously"""
        # List experiments
        experiments = experiment_api.list(page=1, page_size=5)
        
        # Validate response structure
        assert hasattr(experiments, 'experiments')
        assert hasattr(experiments, 'total')
        assert hasattr(experiments, 'page')
        assert hasattr(experiments, 'page_size')
        assert isinstance(experiments.experiments, list)
        assert isinstance(experiments.total, int)

    @pytest.mark.asyncio
    async def test_list_experiments_async(self, experiment_api):
        """Test listing experiments asynchronously"""
        # List experiments
        experiments = await experiment_api.alist(page=1, page_size=5)
        
        # Validate response structure
        assert hasattr(experiments, 'experiments')
        assert hasattr(experiments, 'total')
        assert hasattr(experiments, 'page')
        assert hasattr(experiments, 'page_size')
        assert isinstance(experiments.experiments, list)
        assert isinstance(experiments.total, int)

    def test_get_experiment_sync(self, experiment_api, test_column, test_row):
        """Test retrieving a specific experiment synchronously"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Create experiment first
        experiment_data = ExperimentCreate(
            name=f"SDK_TEST_Get_{timestamp}",
            description="Test experiment for get operation",
            columns=[test_column],
            rows=[test_row]
        )
        created_experiment = experiment_api.create(experiment_data)
        
        try:
            # Get experiment
            retrieved_experiment = experiment_api.get(created_experiment.id)
            
            # Validate response
            assert retrieved_experiment.id == created_experiment.id
            assert retrieved_experiment.name == created_experiment.name
            assert retrieved_experiment.description == created_experiment.description
            
        finally:
            # Clean up
            experiment_api.delete(created_experiment.id)

    @pytest.mark.asyncio
    async def test_get_experiment_async(self, experiment_api, test_column, test_row):
        """Test retrieving a specific experiment asynchronously"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Create experiment first
        experiment_data = ExperimentCreate(
            name=f"SDK_TEST_Async_Get_{timestamp}",
            description="Async test experiment for get operation",
            columns=[test_column],
            rows=[test_row]
        )
        created_experiment = await experiment_api.acreate(experiment_data)
        
        try:
            # Get experiment
            retrieved_experiment = await experiment_api.aget(created_experiment.id)
            
            # Validate response
            assert retrieved_experiment.id == created_experiment.id
            assert retrieved_experiment.name == created_experiment.name
            assert retrieved_experiment.description == created_experiment.description
            
        finally:
            # Clean up
            await experiment_api.adelete(created_experiment.id)


class TestExperimentRowManagement:
    """Test row management operations"""
    
    def test_add_rows_sync(self, experiment_api, test_column, test_row):
        """Test adding rows to an experiment synchronously"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Create experiment first
        experiment_data = ExperimentCreate(
            name=f"SDK_TEST_AddRows_{timestamp}",
            description="Test experiment for adding rows",
            columns=[test_column],
            rows=[test_row]
        )
        experiment = experiment_api.create(experiment_data)
        
        try:
            # Add more rows
            new_rows = [
                ExperimentRowType(
                    input={"user_input": "What is 3+3?"},
                    ideal_output="6"
                ),
                ExperimentRowType(
                    input={"user_input": "What is the capital of France?"},
                    ideal_output="Paris"
                )
            ]
            
            add_request = AddExperimentRowsRequest(rows=new_rows)
            result = experiment_api.add_rows(experiment.id, add_request)
            
            # Validate response
            assert "message" in result
            
            # Verify rows were added by getting the experiment
            updated_experiment = experiment_api.get(experiment.id)
            assert len(updated_experiment.rows) == 3  # Original 1 + 2 new
            
        finally:
            # Clean up
            experiment_api.delete(experiment.id)

    @pytest.mark.asyncio
    async def test_add_rows_async(self, experiment_api, test_column, test_row):
        """Test adding rows to an experiment asynchronously"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Create experiment first
        experiment_data = ExperimentCreate(
            name=f"SDK_TEST_Async_AddRows_{timestamp}",
            description="Async test experiment for adding rows",
            columns=[test_column],
            rows=[test_row]
        )
        experiment = await experiment_api.acreate(experiment_data)
        
        try:
            # Add more rows
            new_rows = [
                ExperimentRowType(
                    input={"user_input": "What is 5+5?"},
                    ideal_output="10"
                )
            ]
            
            add_request = AddExperimentRowsRequest(rows=new_rows)
            result = await experiment_api.aadd_rows(experiment.id, add_request)
            
            # Validate response
            assert "message" in result
            
            # Verify rows were added
            updated_experiment = await experiment_api.aget(experiment.id)
            assert len(updated_experiment.rows) == 2  # Original 1 + 1 new
            
        finally:
            # Clean up
            await experiment_api.adelete(experiment.id)


class TestExperimentColumnManagement:
    """Test column management operations"""
    
    def test_add_columns_sync(self, experiment_api, test_column, test_row):
        """Test adding columns to an experiment synchronously"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Create experiment first
        experiment_data = ExperimentCreate(
            name=f"SDK_TEST_AddColumns_{timestamp}",
            description="Test experiment for adding columns",
            columns=[test_column],
            rows=[test_row]
        )
        experiment = experiment_api.create(experiment_data)
        
        try:
            # Add more columns
            new_column = ExperimentColumnType(
                model="gpt-4",
                name="SDK Test GPT-4 Column",
                temperature=0.3,
                max_completion_tokens=300,
                top_p=1.0,
                frequency_penalty=0.0,
                presence_penalty=0.0,
                prompt_messages=[
                    {
                        "role": "system",
                        "content": "You are an expert assistant for SDK testing."
                    },
                    {
                        "role": "user",
                        "content": "{{user_input}}"
                    }
                ],
                tools=[],
                tool_choice="auto",
                response_format={"type": "text"}
            )
            
            add_request = AddExperimentColumnsRequest(columns=[new_column])
            result = experiment_api.add_columns(experiment.id, add_request)
            
            # Validate response
            assert "message" in result
            
            # Verify columns were added
            updated_experiment = experiment_api.get(experiment.id)
            assert len(updated_experiment.columns) == 2  # Original 1 + 1 new
            
        finally:
            # Clean up
            experiment_api.delete(experiment.id)

    @pytest.mark.asyncio
    async def test_add_columns_async(self, experiment_api, test_column, test_row):
        """Test adding columns to an experiment asynchronously"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Create experiment first
        experiment_data = ExperimentCreate(
            name=f"SDK_TEST_Async_AddColumns_{timestamp}",
            description="Async test experiment for adding columns",
            columns=[test_column],
            rows=[test_row]
        )
        experiment = await experiment_api.acreate(experiment_data)
        
        try:
            # Add more columns
            new_column = ExperimentColumnType(
                model="gpt-4",
                name="SDK Test Async GPT-4 Column",
                temperature=0.5,
                max_completion_tokens=400,
                top_p=1.0,
                frequency_penalty=0.0,
                presence_penalty=0.0,
                prompt_messages=[
                    {
                        "role": "system",
                        "content": "You are a precise assistant for async SDK testing."
                    },
                    {
                        "role": "user",
                        "content": "{{user_input}}"
                    }
                ],
                tools=[],
                tool_choice="auto",
                response_format={"type": "text"}
            )
            
            add_request = AddExperimentColumnsRequest(columns=[new_column])
            result = await experiment_api.aadd_columns(experiment.id, add_request)
            
            # Validate response
            assert "message" in result
            
            # Verify columns were added
            updated_experiment = await experiment_api.aget(experiment.id)
            assert len(updated_experiment.columns) == 2  # Original 1 + 1 new
            
        finally:
            # Clean up
            await experiment_api.adelete(experiment.id)


class TestExperimentExecution:
    """Test experiment execution operations"""
    
    def test_run_experiment_sync(self, experiment_api, test_column, test_row):
        """Test running an experiment synchronously"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Create experiment first
        experiment_data = ExperimentCreate(
            name=f"SDK_TEST_Run_{timestamp}",
            description="Test experiment for running",
            columns=[test_column],
            rows=[test_row]
        )
        experiment = experiment_api.create(experiment_data)
        
        try:
            # Run experiment
            result = experiment_api.run_experiment(experiment.id)
            
            # Validate response
            assert "message" in result or "experiment_id" in result
            
        finally:
            # Clean up
            experiment_api.delete(experiment.id)

    @pytest.mark.asyncio
    async def test_run_experiment_async(self, experiment_api, test_column, test_row):
        """Test running an experiment asynchronously"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Create experiment first
        experiment_data = ExperimentCreate(
            name=f"SDK_TEST_Async_Run_{timestamp}",
            description="Async test experiment for running",
            columns=[test_column],
            rows=[test_row]
        )
        experiment = await experiment_api.acreate(experiment_data)
        
        try:
            # Run experiment
            result = await experiment_api.arun_experiment(experiment.id)
            
            # Validate response
            assert "message" in result or "experiment_id" in result
            
        finally:
            # Clean up
            await experiment_api.adelete(experiment.id)

    def test_run_experiment_evals_sync(self, experiment_api, test_column, test_row):
        """Test running experiment evaluations synchronously"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Create experiment first
        experiment_data = ExperimentCreate(
            name=f"SDK_TEST_RunEvals_{timestamp}",
            description="Test experiment for running evaluations",
            columns=[test_column],
            rows=[test_row]
        )
        experiment = experiment_api.create(experiment_data)
        
        try:
            # Run evaluations
            evals_request = RunExperimentEvalsRequest(
                evaluator_slugs=["is_english"]  # Using a common evaluator
            )
            result = experiment_api.run_experiment_evals(experiment.id, evals_request)
            
            # Validate response
            assert "message" in result or "experiment_id" in result
            
        finally:
            # Clean up
            experiment_api.delete(experiment.id)

    @pytest.mark.asyncio
    async def test_run_experiment_evals_async(self, experiment_api, test_column, test_row):
        """Test running experiment evaluations asynchronously"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Create experiment first
        experiment_data = ExperimentCreate(
            name=f"SDK_TEST_Async_RunEvals_{timestamp}",
            description="Async test experiment for running evaluations",
            columns=[test_column],
            rows=[test_row]
        )
        experiment = await experiment_api.acreate(experiment_data)
        
        try:
            # Run evaluations
            evals_request = RunExperimentEvalsRequest(
                evaluator_slugs=["is_english"]  # Using a common evaluator
            )
            result = await experiment_api.arun_experiment_evals(experiment.id, evals_request)
            
            # Validate response
            assert "message" in result or "experiment_id" in result
            
        finally:
            # Clean up
            await experiment_api.adelete(experiment.id)


class TestExperimentWorkflow:
    """Test complete experiment workflows"""
    
    @pytest.mark.asyncio
    async def test_complete_experiment_workflow_async(self, experiment_api, test_column, test_row):
        """Test a complete experiment workflow asynchronously"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Step 1: Create experiment
        experiment_data = ExperimentCreate(
            name=f"SDK_TEST_Workflow_{timestamp}",
            description="Complete workflow test experiment",
            columns=[test_column],
            rows=[test_row]
        )
        experiment = await experiment_api.acreate(experiment_data)
        
        try:
            # Step 2: Add more rows
            new_rows = [
                ExperimentRowType(
                    input={"user_input": "What is machine learning?"}
                )
            ]
            add_rows_request = AddExperimentRowsRequest(rows=new_rows)
            await experiment_api.aadd_rows(experiment.id, add_rows_request)
            
            # Step 3: Add more columns
            new_column = ExperimentColumnType(
                model="gpt-4",
                name="Workflow Test GPT-4",
                temperature=0.2,
                max_completion_tokens=200,
                top_p=1.0,
                frequency_penalty=0.0,
                presence_penalty=0.0,
                prompt_messages=[
                    {
                        "role": "system",
                        "content": "You are a concise assistant."
                    },
                    {
                        "role": "user",
                        "content": "{{user_input}}"
                    }
                ],
                tools=[],
                tool_choice="auto",
                response_format={"type": "text"}
            )
            add_columns_request = AddExperimentColumnsRequest(columns=[new_column])
            await experiment_api.aadd_columns(experiment.id, add_columns_request)
            
            # Step 4: Verify final state
            final_experiment = await experiment_api.aget(experiment.id)
            assert len(final_experiment.rows) == 2  # Original + 1 new
            assert len(final_experiment.columns) == 2  # Original + 1 new
            
            # Step 5: Run experiment (optional - may take time)
            # run_result = await experiment_api.arun_experiment(experiment.id)
            # assert "message" in run_result or "experiment_id" in run_result
            
        finally:
            # Clean up
            await experiment_api.adelete(experiment.id)