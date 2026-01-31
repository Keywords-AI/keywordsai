"""
Keywords AI Experiment APIs

This module provides functionality for managing experiments, including:
- Creating and managing experiments with columns and rows
- Adding/removing/updating experiment rows and columns
- Running experiments and evaluations
- Listing and retrieving experiment information
"""

from typing import Optional, Dict, Any, List, Union
from respan.types.experiment_types import (
    Experiment,
    ExperimentList,
    ExperimentCreate,
    ExperimentUpdate,
    AddExperimentRowsRequest,
    RemoveExperimentRowsRequest,
    UpdateExperimentRowsRequest,
    AddExperimentColumnsRequest,
    RemoveExperimentColumnsRequest,
    UpdateExperimentColumnsRequest,
    RunExperimentRequest,
    RunExperimentEvalsRequest,
)
from respan.utils.base import BaseAPI
from respan.constants.experiment_constants import (
    EXPERIMENT_BASE_PATH,
    EXPERIMENT_CREATION_PATH,
    EXPERIMENT_LIST_PATH,
    EXPERIMENT_GET_PATH,
    EXPERIMENT_UPDATE_PATH,
    EXPERIMENT_ADD_ROWS_PATH,
    EXPERIMENT_REMOVE_ROWS_PATH,
    EXPERIMENT_UPDATE_ROWS_PATH,
    EXPERIMENT_ADD_COLUMNS_PATH,
    EXPERIMENT_REMOVE_COLUMNS_PATH,
    EXPERIMENT_UPDATE_COLUMNS_PATH,
    EXPERIMENT_RUN_PATH,
    EXPERIMENT_RUN_EVALS_PATH,
)


class ExperimentAPI(BaseAPI[Experiment, ExperimentList, ExperimentCreate, ExperimentUpdate]):
    """
    Unified Experiment API client for Keywords AI with both sync and async methods.

    This class provides comprehensive functionality for managing experiments in Keywords AI,
    including creating experiments, managing columns and rows, running experiments,
    and running evaluations. All operations are available in both synchronous and
    asynchronous variants.

    Features:
        - Create and manage experiments with custom configurations
        - Add/remove/update experiment rows (test cases)
        - Add/remove/update experiment columns (model configurations)
        - Run experiments to generate outputs
        - Run evaluations on experiment results
        - Full CRUD operations for experiment management

    Args:
        api_key (str): Your Keywords AI API key. Required for authentication.
        base_url (str, optional): Base URL for the Keywords AI API.
            Defaults to the standard Keywords AI API endpoint.

    Example (Synchronous):
        >>> from respan.experiments.api import ExperimentAPI
        >>> from respan.types.experiment_types import ExperimentCreate, ExperimentColumnType, ExperimentRowType
        >>>
        >>> # Initialize the client
        >>> client = ExperimentAPI(api_key="your-api-key")
        >>>
        >>> # Create a new experiment (synchronous - no await)
        >>> experiment_data = ExperimentCreate(
        ...     name="My Test Experiment",
        ...     description="Experiment for testing different prompts",
        ...     columns=[
        ...         ExperimentColumnType(
        ...             model="gpt-3.5-turbo",
        ...             name="Version A",
        ...             temperature=0.7,
        ...             max_completion_tokens=256,
        ...             top_p=1.0,
        ...             frequency_penalty=0.0,
        ...             presence_penalty=0.0,
        ...             prompt_messages=[
        ...                 {"role": "system", "content": "You are a helpful assistant."},
        ...                 {"role": "user", "content": "{{user_input}}"}
        ...             ]
        ...         )
        ...     ],
        ...     rows=[
        ...         ExperimentRowType(
        ...             input={"user_input": "What is the weather like?"}
        ...         )
        ...     ]
        ... )
        >>> experiment = client.create(experiment_data)
        >>> print(f"Created experiment: {experiment.name}")

    Example (Asynchronous):
        >>> import asyncio
        >>> from respan.experiments.api import ExperimentAPI
        >>>
        >>> async def main():
        ...     # Initialize the client
        ...     client = ExperimentAPI(api_key="your-api-key")
        ...
        ...     # Create a new experiment (asynchronous - with await)
        ...     experiment = await client.acreate(experiment_data)
        ...     print(f"Created experiment: {experiment.name}")
        >>>
        >>> asyncio.run(main())

    Note:
        - Use await client.amethod() for asynchronous operations
        - Use client.method() for synchronous operations
    """

    def __init__(self, api_key: str, base_url: str = None):
        """
        Initialize the Experiment API client.

        Args:
            api_key (str): Your Keywords AI API key for authentication
            base_url (str, optional): Custom base URL for the API. If not provided,
                uses the default Keywords AI API endpoint.
        """
        super().__init__(api_key, base_url)

    # Asynchronous methods (with "a" prefix)
    async def acreate(self, create_data: Union[Dict[str, Any], ExperimentCreate]) -> Experiment:
        """
        Create a new experiment with specified parameters (asynchronous).

        This method creates a new experiment in Keywords AI with the provided configuration.
        The experiment includes columns (model configurations) and rows (test cases).

        Args:
            create_data (Union[Dict[str, Any], ExperimentCreate]): Experiment creation parameters including:
                - name (str): Name of the experiment
                - description (str): Description of the experiment's purpose
                - columns (List[ExperimentColumnType]): List of column configurations
                - rows (List[ExperimentRowType], optional): List of test cases

        Returns:
            Experiment: The created experiment object containing:
                - id (str): Unique identifier for the experiment
                - name (str): Experiment name
                - description (str): Experiment description
                - columns (List[ExperimentColumnType]): Column configurations
                - rows (List[ExperimentRowType]): Test cases
                - status (str): Current status of the experiment
                - created_at (str): Creation timestamp

        Raises:
            RespanError: If the experiment creation fails due to invalid parameters
                or API errors

        Example:
            >>> from respan.types.experiment_types import ExperimentCreate, ExperimentColumnType
            >>>
            >>> experiment_data = ExperimentCreate(
            ...     name="Prompt Comparison Test",
            ...     description="Compare different system prompts",
            ...     columns=[
            ...         ExperimentColumnType(
            ...             model="gpt-3.5-turbo",
            ...             name="Formal Assistant",
            ...             temperature=0.3,
            ...             max_completion_tokens=200,
            ...             top_p=1.0,
            ...             frequency_penalty=0.0,
            ...             presence_penalty=0.0,
            ...             prompt_messages=[
            ...                 {"role": "system", "content": "You are a formal, professional assistant."}
            ...             ]
            ...         )
            ...     ]
            ... )
            >>> experiment = await client.acreate(experiment_data)
        """
        # Validate and prepare the input data
        validated_data = self._validate_input(create_data, ExperimentCreate)
        
        response = await self.client.post(
            EXPERIMENT_CREATION_PATH,
            json_data=self._prepare_json_data(validated_data),
        )
        return Experiment(**response)

    async def alist(
        self, page: Optional[int] = None, page_size: Optional[int] = None, **filters
    ) -> ExperimentList:
        """
        List experiments with optional filtering and pagination (asynchronous).

        Retrieve a paginated list of experiments, optionally filtered by various criteria.
        This method supports filtering by experiment properties and provides pagination
        for handling large numbers of experiments.

        Args:
            page (int, optional): Page number for pagination (1-based).
                Defaults to 1 if not specified.
            page_size (int, optional): Number of experiments per page.
                Defaults to API default (usually 20) if not specified.
            **filters: Additional filter parameters such as:
                - name (str): Filter by experiment name (partial match)
                - status (str): Filter by experiment status
                - created_after (str): Filter experiments created after this date
                - created_before (str): Filter experiments created before this date

        Returns:
            ExperimentList: A paginated list containing:
                - experiments (List[Experiment]): List of experiment objects
                - total (int): Total number of experiments matching filters
                - page (int): Current page number
                - page_size (int): Number of items per page

        Example:
            >>> # List all experiments
            >>> experiments = await client.alist()
            >>> print(f"Found {experiments.total} experiments")
            >>>
            >>> # List with pagination
            >>> page1 = await client.alist(page=1, page_size=10)
            >>>
            >>> # List with filters
            >>> recent_experiments = await client.alist(
            ...     created_after="2024-01-01T00:00:00Z"
            ... )
        """
        params = {}
        if page is not None:
            params["page"] = page
        if page_size is not None:
            params["page_size"] = page_size
        params.update(filters)

        response = await self.client.get(EXPERIMENT_LIST_PATH, params=params)
        return ExperimentList(**response)

    async def aget(self, resource_id: str) -> Experiment:
        """
        Retrieve a specific experiment by its unique identifier (asynchronous).

        Fetch detailed information about an experiment including its current status,
        columns, rows, and results. This is useful for checking experiment progress
        and retrieving results.

        Args:
            resource_id (str): The unique identifier of the experiment to retrieve.
                This is typically returned when creating an experiment or listing experiments.

        Returns:
            Experiment: Complete experiment information including:
                - id (str): Unique experiment identifier
                - name (str): Experiment name
                - description (str): Experiment description
                - columns (List[ExperimentColumnType]): Column configurations
                - rows (List[ExperimentRowType]): Test cases with results
                - status (str): Current status ("ready", "running", "completed", etc.)
                - created_at (str): Creation timestamp
                - updated_at (str): Last update timestamp

        Raises:
            RespanError: If the experiment is not found or access is denied

        Example:
            >>> # Get experiment details
            >>> experiment = await client.aget("experiment-123")
            >>> print(f"Experiment '{experiment.name}' status: {experiment.status}")
            >>>
            >>> # Check if experiment has results
            >>> for row in experiment.rows:
            ...     if row.results:
            ...         print(f"Row {row.id} has {len(row.results)} results")
        """
        response = await self.client.get(f"{EXPERIMENT_GET_PATH}/{resource_id}")
        return Experiment(**response)

    async def adelete(self, resource_id: str) -> Dict[str, Any]:
        """
        Delete an experiment permanently (asynchronous).

        WARNING: This operation is irreversible. The experiment and all its associated
        data will be permanently deleted.

        Args:
            resource_id (str): The unique identifier of the experiment to delete

        Returns:
            Dict[str, Any]: API response confirming deletion, typically containing:
                - message (str): Confirmation message
                - deleted_at (str): Timestamp of deletion

        Raises:
            RespanError: If the experiment is not found or deletion fails

        Example:
            >>> # Delete an experiment (be careful!)
            >>> response = await client.adelete("experiment-123")
            >>> print(response["message"])  # "Experiment deleted successfully"

        Note:
            Consider exporting important results before deletion as this operation
            cannot be undone.
        """
        return await self.client.delete(f"{EXPERIMENT_BASE_PATH}/{resource_id}")

    async def aupdate(self, resource_id: str, update_data: Union[Dict[str, Any], ExperimentUpdate]) -> Experiment:
        """
        Update an existing experiment's metadata (asynchronous).

        Modify experiment properties such as name and description. Note that core
        experiment structure (columns and rows) should be updated using the specific
        row and column management methods.

        Args:
            resource_id (str): The unique identifier of the experiment to update
            update_data (Union[Dict[str, Any], ExperimentUpdate]): Update parameters containing:
                - name (str, optional): New name for the experiment
                - description (str, optional): New description for the experiment

        Returns:
            Experiment: The updated experiment object with new properties applied

        Raises:
            RespanError: If the experiment is not found, update fails, or
                invalid parameters are provided

        Example:
            >>> from respan.types.experiment_types import ExperimentUpdate
            >>>
            >>> # Update experiment name and description
            >>> update_data = ExperimentUpdate(
            ...     name="Updated Experiment Name",
            ...     description="Updated description with more details"
            ... )
            >>> updated_experiment = await client.aupdate("experiment-123", update_data)
            >>> print(f"Updated experiment: {updated_experiment.name}")
        """
                # Validate and prepare the input data
        validated_data = self._validate_input(update_data, ExperimentUpdate, partial=True)

        response = await self.client.patch(
            f"{EXPERIMENT_UPDATE_PATH}/{resource_id}",
            json_data=self._prepare_json_data(validated_data, partial=True),
        )
        return Experiment(**response)

    # Synchronous methods (without "a" prefix)
    def create(self, create_data: Union[Dict[str, Any], ExperimentCreate]) -> Experiment:
        """Create a new experiment with specified parameters (synchronous)."""
        # Validate and prepare the input data
        validated_data = self._validate_input(create_data, ExperimentCreate)
        
        response = self.sync_client.post(
            EXPERIMENT_CREATION_PATH,
            json_data=self._prepare_json_data(validated_data),
        )
        return Experiment(**response)

    def list(
        self, page: Optional[int] = None, page_size: Optional[int] = None, **filters
    ) -> ExperimentList:
        """List experiments with optional filtering and pagination (synchronous)."""
        params = {}
        if page is not None:
            params["page"] = page
        if page_size is not None:
            params["page_size"] = page_size
        params.update(filters)

        response = self.sync_client.get(EXPERIMENT_LIST_PATH, params=params)
        return ExperimentList(**response)

    def get(self, resource_id: str) -> Experiment:
        """Retrieve a specific experiment by its unique identifier (synchronous)."""
        response = self.sync_client.get(f"{EXPERIMENT_GET_PATH}/{resource_id}")
        return Experiment(**response)

    def delete(self, resource_id: str) -> Dict[str, Any]:
        """Delete an experiment permanently (synchronous)."""
        return self.sync_client.delete(f"{EXPERIMENT_BASE_PATH}/{resource_id}")

    def update(self, resource_id: str, update_data: Union[Dict[str, Any], ExperimentUpdate]) -> Experiment:
        """Update an existing experiment's metadata (synchronous)."""
                # Validate and prepare the input data
        validated_data = self._validate_input(update_data, ExperimentUpdate, partial=True)

        response = self.sync_client.patch(
            f"{EXPERIMENT_UPDATE_PATH}/{resource_id}",
            json_data=self._prepare_json_data(validated_data, partial=True),
        )
        return Experiment(**response)

    # Row management methods (both sync and async variants)
    async def aadd_rows(
        self, experiment_id: str, rows_request: Union[Dict[str, Any], AddExperimentRowsRequest]
    ) -> Dict[str, Any]:
        """
        Add rows to an existing experiment (asynchronous).

        This method allows you to add new test cases to an experiment. Each row
        represents a different input scenario that will be tested against all columns.

        Args:
            experiment_id (str): The unique identifier of the target experiment
            rows_request (AddExperimentRowsRequest): Request containing:
                - rows (List[ExperimentRowType]): List of rows to add, each containing:
                    - input (Dict[str, Any]): Input variables for the test case
                    - ideal_output (str, optional): Expected output for evaluation

        Returns:
            Dict[str, Any]: Response containing:
                - message (str): Success message
                - added_rows (int): Number of rows added
                - experiment_id (str): ID of the updated experiment

        Raises:
            RespanError: If the experiment is not found or request is invalid

        Example:
            >>> from respan.types.experiment_types import AddExperimentRowsRequest, ExperimentRowType
            >>>
            >>> rows_request = AddExperimentRowsRequest(
            ...     rows=[
            ...         ExperimentRowType(
            ...             input={"user_question": "What is machine learning?"}
            ...         ),
            ...         ExperimentRowType(
            ...             input={"user_question": "Explain neural networks"},
            ...             ideal_output="A neural network is..."
            ...         )
            ...     ]
            ... )
            >>> result = await client.aadd_rows("experiment-123", rows_request)
            >>> print(f"Added {result['added_rows']} rows to experiment")
        """
        # Validate and prepare the input data
        validated_data = self._validate_input(rows_request, AddExperimentRowsRequest)
        
        return await self.client.post(
            EXPERIMENT_ADD_ROWS_PATH(experiment_id),
            json_data=self._prepare_json_data(validated_data),
        )

    def add_rows(
        self, experiment_id: str, rows_request: Union[Dict[str, Any], AddExperimentRowsRequest]
    ) -> Dict[str, Any]:
        """Add rows to an existing experiment (synchronous)."""
        # Validate and prepare the input data
        validated_data = self._validate_input(rows_request, AddExperimentRowsRequest)
        
        return self.sync_client.post(
            EXPERIMENT_ADD_ROWS_PATH(experiment_id),
            json_data=self._prepare_json_data(validated_data),
        )

    async def aremove_rows(
        self, experiment_id: str, rows_request: Union[Dict[str, Any], RemoveExperimentRowsRequest]
    ) -> Dict[str, Any]:
        """
        Remove rows from an experiment (asynchronous).

        Remove specific test cases from an experiment by their IDs.

        Args:
            experiment_id (str): The unique identifier of the target experiment
            rows_request (Union[Dict[str, Any], RemoveExperimentRowsRequest]): Request containing:
                - rows (List[str]): List of row IDs to remove

        Returns:
            Dict[str, Any]: Response containing:
                - message (str): Success message
                - removed_rows (int): Number of rows removed

        Example:
            >>> from respan.types.experiment_types import RemoveExperimentRowsRequest
            >>>
            >>> remove_request = RemoveExperimentRowsRequest(
            ...     rows=["row-id-1", "row-id-2"]
            ... )
            >>> result = await client.aremove_rows("experiment-123", remove_request)
        """
        # Validate and prepare the input data
        validated_data = self._validate_input(rows_request, RemoveExperimentRowsRequest)
        return await self.client.delete(
            EXPERIMENT_REMOVE_ROWS_PATH(experiment_id),
            json_data=self._prepare_json_data(validated_data),
        )

    def remove_rows(
        self, experiment_id: str, rows_request: Union[Dict[str, Any], RemoveExperimentRowsRequest]
    ) -> Dict[str, Any]:
        """Remove rows from an experiment (synchronous)."""
        # Validate and prepare the input data
        validated_data = self._validate_input(rows_request, RemoveExperimentRowsRequest)
        
        return self.sync_client.delete(
            EXPERIMENT_REMOVE_ROWS_PATH(experiment_id),
            json_data=self._prepare_json_data(validated_data),
        )

    async def aupdate_rows(
        self, experiment_id: str, rows_request: Union[Dict[str, Any], UpdateExperimentRowsRequest]
    ) -> Dict[str, Any]:
        """
        Update existing rows in an experiment (asynchronous).

        Modify the input data or ideal outputs for existing test cases.

        Args:
            experiment_id (str): The unique identifier of the target experiment
            rows_request (Union[Dict[str, Any], UpdateExperimentRowsRequest]): Request containing:
                - rows (List[ExperimentRowType]): List of rows to update with their IDs

        Returns:
            Dict[str, Any]: Response containing:
                - message (str): Success message
                - updated_rows (int): Number of rows updated

        Example:
            >>> from respan.types.experiment_types import UpdateExperimentRowsRequest, ExperimentRowType
            >>>
            >>> update_request = UpdateExperimentRowsRequest(
            ...     rows=[
            ...         ExperimentRowType(
            ...             id="existing-row-id",
            ...             input={"user_question": "Updated question"}
            ...         )
            ...     ]
            ... )
            >>> result = await client.aupdate_rows("experiment-123", update_request)
        """
        # Validate and prepare the input data
        validated_data = self._validate_input(rows_request, UpdateExperimentRowsRequest)
        
        return await self.client.patch(
            EXPERIMENT_UPDATE_ROWS_PATH(experiment_id),
            json_data=self._prepare_json_data(validated_data),
        )

    def update_rows(
        self, experiment_id: str, rows_request: Union[Dict[str, Any], UpdateExperimentRowsRequest]
    ) -> Dict[str, Any]:
        """Update existing rows in an experiment (synchronous)."""
        # Validate and prepare the input data
        validated_data = self._validate_input(rows_request, UpdateExperimentRowsRequest)
        
        return self.sync_client.patch(
            EXPERIMENT_UPDATE_ROWS_PATH(experiment_id),
            json_data=self._prepare_json_data(validated_data),
        )

    # Column management methods (both sync and async variants)
    async def aadd_columns(
        self, experiment_id: str, columns_request: Union[Dict[str, Any], AddExperimentColumnsRequest]
    ) -> Dict[str, Any]:
        """
        Add columns to an existing experiment (asynchronous).

        Add new model configurations to test against existing rows.

        Args:
            experiment_id (str): The unique identifier of the target experiment
            columns_request (Union[Dict[str, Any], AddExperimentColumnsRequest]): Request containing:
                - columns (List[ExperimentColumnType]): List of column configurations to add

        Returns:
            Dict[str, Any]: Response containing:
                - message (str): Success message
                - added_columns (int): Number of columns added

        Example:
            >>> from respan.types.experiment_types import AddExperimentColumnsRequest, ExperimentColumnType
            >>>
            >>> columns_request = AddExperimentColumnsRequest(
            ...     columns=[
            ...         ExperimentColumnType(
            ...             model="gpt-4",
            ...             name="GPT-4 Version",
            ...             temperature=0.5,
            ...             max_completion_tokens=300,
            ...             top_p=1.0,
            ...             frequency_penalty=0.0,
            ...             presence_penalty=0.0,
            ...             prompt_messages=[
            ...                 {"role": "system", "content": "You are an expert assistant."}
            ...             ]
            ...         )
            ...     ]
            ... )
            >>> result = await client.aadd_columns("experiment-123", columns_request)
        """
        # Validate and prepare the input data
        validated_data = self._validate_input(columns_request, AddExperimentColumnsRequest)
        
        return await self.client.post(
            EXPERIMENT_ADD_COLUMNS_PATH(experiment_id),
            json_data=self._prepare_json_data(validated_data),
        )

    def add_columns(
        self, experiment_id: str, columns_request: Union[Dict[str, Any], AddExperimentColumnsRequest]
    ) -> Dict[str, Any]:
        """Add columns to an existing experiment (synchronous)."""
        # Validate and prepare the input data
        validated_data = self._validate_input(columns_request, AddExperimentColumnsRequest)
        
        return self.sync_client.post(
            EXPERIMENT_ADD_COLUMNS_PATH(experiment_id),
            json_data=self._prepare_json_data(validated_data),
        )

    async def aremove_columns(
        self, experiment_id: str, columns_request: Union[Dict[str, Any], RemoveExperimentColumnsRequest]
    ) -> Dict[str, Any]:
        """
        Remove columns from an experiment (asynchronous).

        Remove specific model configurations from an experiment by their IDs.

        Args:
            experiment_id (str): The unique identifier of the target experiment
            columns_request (Union[Dict[str, Any], RemoveExperimentColumnsRequest]): Request containing:
                - columns (List[str]): List of column IDs to remove

        Returns:
            Dict[str, Any]: Response containing:
                - message (str): Success message
                - removed_columns (int): Number of columns removed

        Example:
            >>> from respan.types.experiment_types import RemoveExperimentColumnsRequest
            >>>
            >>> remove_request = RemoveExperimentColumnsRequest(
            ...     columns=["column-id-1", "column-id-2"]
            ... )
            >>> result = await client.aremove_columns("experiment-123", remove_request)
        """
        # Validate and prepare the input data
        validated_data = self._validate_input(columns_request, RemoveExperimentColumnsRequest)
        
        return await self.client.delete(
            EXPERIMENT_REMOVE_COLUMNS_PATH(experiment_id),
            json_data=self._prepare_json_data(validated_data),
        )

    def remove_columns(
        self, experiment_id: str, columns_request: Union[Dict[str, Any], RemoveExperimentColumnsRequest]
    ) -> Dict[str, Any]:
        """Remove columns from an experiment (synchronous)."""
        # Validate and prepare the input data
        validated_data = self._validate_input(columns_request, RemoveExperimentColumnsRequest)
        
        return self.sync_client.delete(
            EXPERIMENT_REMOVE_COLUMNS_PATH(experiment_id),
            json_data=self._prepare_json_data(validated_data),
        )

    async def aupdate_columns(
        self, experiment_id: str, columns_request: Union[Dict[str, Any], UpdateExperimentColumnsRequest]
    ) -> Dict[str, Any]:
        """
        Update existing columns in an experiment (asynchronous).

        Modify the configuration of existing model columns.

        Args:
            experiment_id (str): The unique identifier of the target experiment
            columns_request (Union[Dict[str, Any], UpdateExperimentColumnsRequest]): Request containing:
                - columns (List[ExperimentColumnType]): List of columns to update

        Returns:
            Dict[str, Any]: Response containing:
                - message (str): Success message
                - updated_columns (int): Number of columns updated

        Example:
            >>> from respan.types.experiment_types import UpdateExperimentColumnsRequest, ExperimentColumnType
            >>>
            >>> update_request = UpdateExperimentColumnsRequest(
            ...     columns=[
            ...         ExperimentColumnType(
            ...             id="existing-column-id",
            ...             model="gpt-4",
            ...             name="Updated GPT-4 Config",
            ...             temperature=0.3,
            ...             max_completion_tokens=400,
            ...             top_p=1.0,
            ...             frequency_penalty=0.0,
            ...             presence_penalty=0.0
            ...         )
            ...     ]
            ... )
            >>> result = await client.aupdate_columns("experiment-123", update_request)
        """
        # Validate and prepare the input data
        validated_data = self._validate_input(columns_request, UpdateExperimentColumnsRequest)
        
        return await self.client.patch(
            EXPERIMENT_UPDATE_COLUMNS_PATH(experiment_id),
            json_data=self._prepare_json_data(validated_data),
        )

    def update_columns(
        self, experiment_id: str, columns_request: Union[Dict[str, Any], UpdateExperimentColumnsRequest]
    ) -> Dict[str, Any]:
        """Update existing columns in an experiment (synchronous)."""
        # Validate and prepare the input data
        validated_data = self._validate_input(columns_request, UpdateExperimentColumnsRequest)
        
        return self.sync_client.patch(
            EXPERIMENT_UPDATE_COLUMNS_PATH(experiment_id),
            json_data=self._prepare_json_data(validated_data),
        )

    # Experiment execution methods (both sync and async variants)
    async def arun_experiment(
        self, experiment_id: str, run_request: Optional[Union[Dict[str, Any], RunExperimentRequest]] = None
    ) -> Dict[str, Any]:
        """
        Run an experiment to generate outputs (asynchronous).

        Execute the experiment by running all rows against all columns (or specified columns)
        to generate model outputs. This is an asynchronous process.

        Args:
            experiment_id (str): The unique identifier of the experiment to run
            run_request (Union[Dict[str, Any], RunExperimentRequest], optional): Optional request containing:
                - columns (List[ExperimentColumnType], optional): Specific columns to run.
                    If not provided, runs all columns in the experiment.

        Returns:
            Dict[str, Any]: Response containing:
                - message (str): Confirmation message
                - experiment_id (str): ID of the experiment being run
                - status (str): Status of the run ("started", "running", etc.)
                - run_id (str, optional): Unique identifier for this run

        Raises:
            RespanError: If the experiment is not found or cannot be run

        Example:
            >>> # Run entire experiment
            >>> result = await client.arun_experiment("experiment-123")
            >>> print(f"Started experiment run: {result['status']}")
            >>>
            >>> # Run specific columns only
            >>> from respan.types.experiment_types import RunExperimentRequest
            >>> run_request = RunExperimentRequest(
            ...     columns=[specific_column_config]
            ... )
            >>> result = await client.arun_experiment("experiment-123", run_request)

        Note:
            Experiment runs are asynchronous. Use `aget()` to check the status
            and retrieve results when complete.
        """
        request_data = {}
        if run_request:
            # Validate and prepare the input data
            validated_data = self._validate_input(run_request, RunExperimentRequest)
            request_data = self._prepare_json_data(validated_data)
        return await self.client.post(
            EXPERIMENT_RUN_PATH(experiment_id),
            json_data=request_data,
            timeout=600,
        )

    def run_experiment(
        self, experiment_id: str, run_request: Optional[Union[Dict[str, Any], RunExperimentRequest]] = None
    ) -> Dict[str, Any]:
        """Run an experiment to generate outputs (synchronous)."""
        request_data = {}
        if run_request:
            # Validate and prepare the input data
            validated_data = self._validate_input(run_request, RunExperimentRequest)
            request_data = self._prepare_json_data(validated_data)

        return self.sync_client.post(
            EXPERIMENT_RUN_PATH(experiment_id),
            json_data=request_data,
        )

    async def arun_experiment_evals(
        self, experiment_id: str, evals_request: Union[Dict[str, Any], RunExperimentEvalsRequest]
    ) -> Dict[str, Any]:
        """
        Run evaluations on experiment results (asynchronous).

        Execute evaluators on the experiment outputs to generate evaluation scores
        and metrics. This requires that the experiment has been run and has outputs.

        Args:
            experiment_id (str): The unique identifier of the experiment to evaluate
            evals_request (Union[Dict[str, Any], RunExperimentEvalsRequest]): Request containing:
                - evaluator_slugs (List[str]): List of evaluator slugs to use

        Returns:
            Dict[str, Any]: Response containing:
                - message (str): Confirmation message
                - experiment_id (str): ID of the experiment being evaluated
                - evaluators (List[str]): List of evaluators being used
                - status (str): Status of the evaluation

        Raises:
            RespanError: If the experiment is not found, has no outputs,
                or evaluators are invalid

        Example:
            >>> from respan.types.experiment_types import RunExperimentEvalsRequest
            >>>
            >>> evals_request = RunExperimentEvalsRequest(
            ...     evaluator_slugs=["is_english", "relevance_score"]
            ... )
            >>> result = await client.arun_experiment_evals("experiment-123", evals_request)
            >>> print(f"Started evaluation with {len(evals_request.evaluator_slugs)} evaluators")

        Note:
            Evaluations run asynchronously. Use `aget()` to check the status
            and retrieve results when complete.
        """
        # Validate and prepare the input data
        validated_data = self._validate_input(evals_request, RunExperimentEvalsRequest)
        
        return await self.client.post(
            EXPERIMENT_RUN_EVALS_PATH(experiment_id),
            json_data=self._prepare_json_data(validated_data),
        )

    def run_experiment_evals(
        self, experiment_id: str, evals_request: Union[Dict[str, Any], RunExperimentEvalsRequest]
    ) -> Dict[str, Any]:
        """Run evaluations on experiment results (synchronous)."""
        # Validate and prepare the input data
        validated_data = self._validate_input(evals_request, RunExperimentEvalsRequest)
        
        return self.sync_client.post(
            EXPERIMENT_RUN_EVALS_PATH(experiment_id),
            json_data=self._prepare_json_data(validated_data),
        )


def create_experiment_client(api_key: str, base_url: str = None) -> ExperimentAPI:
    """
    Create a unified experiment API client

    Args:
        api_key: Keywords AI API key
        base_url: Base URL for the API (default: KEYWORDS_AI_DEFAULT_BASE_URL)

    Returns:
        ExperimentAPI client instance with both sync and async methods
    """
    return ExperimentAPI(api_key=api_key, base_url=base_url)
