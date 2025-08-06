"""
Real API Integration Tests

These tests use actual API calls against the Keywords AI service.
They require valid credentials in the .env file and a running API server.

Environment variables required:
- KEYWORDSAI_API_KEY
- KEYWORDSAI_BASE_URL (defaults to http://localhost:8000)

Run with: python -m pytest tests/test_keywords_ai_api_integration.py -v -s
"""

import pytest
import os
import asyncio
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv(override=True)

from keywordsai.datasets.api import DatasetAPI, SyncDatasetAPI
from keywordsai.evaluators.api import EvaluatorAPI, SyncEvaluatorAPI
from keywordsai_sdk.keywordsai_types.dataset_types import (
    DatasetCreate,
    DatasetUpdate,
)


@pytest.fixture
def real_api_key():
    """Get real API key from environment"""
    api_key = os.getenv("KEYWORDSAI_API_KEY")
    if not api_key:
        pytest.skip("KEYWORDSAI_API_KEY not found in environment")
    return api_key


@pytest.fixture
def real_base_url():
    """Get real base URL from environment"""
    return os.getenv("KEYWORDSAI_BASE_URL", "http://localhost:8000")


@pytest.fixture
def real_dataset_api(real_api_key, real_base_url):
    """Real dataset API client"""
    return DatasetAPI(api_key=real_api_key, base_url=real_base_url)


@pytest.fixture
def real_sync_dataset_api(real_api_key, real_base_url):
    """Real sync dataset API client"""
    return SyncDatasetAPI(api_key=real_api_key, base_url=real_base_url)


@pytest.fixture
def real_evaluator_api(real_api_key, real_base_url):
    """Real evaluator API client"""
    return EvaluatorAPI(api_key=real_api_key, base_url=real_base_url)


@pytest.fixture
def real_sync_evaluator_api(real_api_key, real_base_url):
    """Real sync evaluator API client"""
    return SyncEvaluatorAPI(api_key=real_api_key, base_url=real_base_url)


@pytest.fixture
def test_dataset_data():
    """Test dataset creation data"""
    now = datetime.utcnow()
    week_ago = now - timedelta(days=7)

    return DatasetCreate(
        name=f"SDK_TEST_{int(now.timestamp())}",
        description="Test dataset created by SDK integration tests",
        type="sampling",
        sampling=10,  # Small sample for testing
        start_time=week_ago.isoformat() + "Z",
        end_time=now.isoformat() + "Z",
    )


class TestKeywordsAIEvaluatorAPIIntegration:
    """Test Keywords AI Evaluator API with real API calls"""

    @pytest.mark.asyncio
    async def test_keywords_ai_list_evaluators_integration(self, real_evaluator_api):
        """Test listing evaluators with real Keywords AI API"""
        print("\n🔍 Testing real evaluator listing...")

        try:
            result = await real_evaluator_api.list(page_size=5)
            print(f"✅ Found {len(result.results)} evaluators")

            assert hasattr(result, "results")
            assert isinstance(result.results, list)

            if result.results:
                evaluator = result.results[0]
                print(f"📋 First evaluator: {evaluator.name} (slug: {evaluator.slug})")
                assert hasattr(evaluator, "id")
                assert hasattr(evaluator, "name")
                assert hasattr(evaluator, "slug")

        except Exception as e:
            print(f"❌ Error listing evaluators: {e}")
            raise

    @pytest.mark.asyncio
    async def test_keywords_ai_get_evaluator_integration(self, real_evaluator_api):
        """Test getting a specific evaluator with real Keywords AI API"""
        print("\n🔍 Testing real evaluator retrieval...")

        try:
            # First get the list to find an evaluator ID
            evaluators = await real_evaluator_api.list(page_size=1)

            if not evaluators.results:
                pytest.skip("No evaluators available to test with")

            evaluator_id = evaluators.results[0].id
            print(f"🎯 Testing with evaluator ID: {evaluator_id}")

            result = await real_evaluator_api.get(evaluator_id)
            print(f"✅ Retrieved evaluator: {result.name}")

            assert result.id == evaluator_id
            assert hasattr(result, "name")
            assert hasattr(result, "slug")

        except Exception as e:
            print(f"❌ Error retrieving evaluator: {e}")
            raise

    def test_keywords_ai_sync_list_evaluators_integration(
        self, real_sync_evaluator_api
    ):
        """Test sync evaluator listing with real Keywords AI API"""
        print("\n🔍 Testing real sync evaluator listing...")

        try:
            result = real_sync_evaluator_api.list(page_size=3)
            print(f"✅ Found {len(result.results)} evaluators (sync)")

            assert hasattr(result, "results")
            assert isinstance(result.results, list)

        except Exception as e:
            print(f"❌ Error listing evaluators (sync): {e}")
            raise


class TestKeywordsAIDatasetAPIIntegration:
    """Test Keywords AI Dataset API with real API calls"""

    @pytest.mark.asyncio
    async def test_keywords_ai_dataset_crud_workflow_integration(
        self, real_dataset_api, test_dataset_data
    ):
        """Test complete dataset CRUD workflow with real Keywords AI API"""
        print("\n🔍 Testing real dataset CRUD workflow...")

        created_dataset = None
        try:
            # 1. Create dataset
            print("📝 Creating dataset...")
            created_dataset = await real_dataset_api.create(test_dataset_data)
            print(f"✅ Created dataset: {created_dataset.id} - {created_dataset.name}")

            assert created_dataset.id is not None
            assert created_dataset.name == test_dataset_data.name
            assert created_dataset.type == test_dataset_data.type

            # 2. Get dataset
            print("📖 Retrieving dataset...")
            retrieved_dataset = await real_dataset_api.get(created_dataset.id)
            print(f"✅ Retrieved dataset: {retrieved_dataset.name}")

            assert retrieved_dataset.id == created_dataset.id
            assert retrieved_dataset.name == created_dataset.name

            # 3. Update dataset
            print("✏️ Updating dataset...")
            update_data = DatasetUpdate(name=f"{test_dataset_data.name}_UPDATED")
            updated_dataset = await real_dataset_api.update(
                created_dataset.id, update_data
            )
            print(f"✅ Updated dataset name: {updated_dataset.name}")

            assert updated_dataset.name.endswith("_UPDATED")

            # 4. List datasets (verify our dataset appears)
            print("📋 Listing datasets...")
            datasets = await real_dataset_api.list(page_size=10)
            print(f"✅ Found {len(datasets.results)} datasets")

            dataset_ids = [d.id for d in datasets.results]
            assert created_dataset.id in dataset_ids

        except Exception as e:
            print(f"❌ Error in dataset CRUD workflow: {e}")
            raise

        finally:
            # Cleanup: Delete the test dataset
            if created_dataset:
                try:
                    print("🗑️ Cleaning up test dataset...")
                    await real_dataset_api.delete(created_dataset.id)
                    print("✅ Test dataset deleted")
                except Exception as cleanup_error:
                    print(
                        f"⚠️ Warning: Could not delete test dataset {created_dataset.id}: {cleanup_error}"
                    )

    @pytest.mark.asyncio
    async def test_dataset_logs_real(self, real_dataset_api, test_dataset_data):
        """Test dataset log operations with real API"""
        print("\n🔍 Testing real dataset log operations...")

        created_dataset = None
        try:
            # Create a test dataset
            print("📝 Creating dataset for log testing...")
            created_dataset = await real_dataset_api.create(test_dataset_data)
            print(f"✅ Created dataset: {created_dataset.id}")

            # List logs in the dataset
            print("📋 Listing dataset logs...")
            logs = await real_dataset_api.list_dataset_logs(
                created_dataset.id, page_size=5
            )
            print(f"✅ Found {len(logs.get('results', []))} logs in dataset")

            # Note: We don't test add/remove logs here as it requires actual log data
            # and specific log IDs which may not be available in the test environment

        except Exception as e:
            print(f"❌ Error in dataset log operations: {e}")
            raise

        finally:
            # Cleanup
            if created_dataset:
                try:
                    await real_dataset_api.delete(created_dataset.id)
                    print("✅ Test dataset deleted")
                except Exception as cleanup_error:
                    print(f"⚠️ Warning: Could not delete test dataset: {cleanup_error}")

    def test_sync_dataset_operations_real(
        self, real_sync_dataset_api, test_dataset_data
    ):
        """Test sync dataset operations with real API"""
        print("\n🔍 Testing real sync dataset operations...")

        created_dataset = None
        try:
            # Test sync dataset creation and listing
            print("📝 Creating dataset (sync)...")
            created_dataset = real_sync_dataset_api.create(test_dataset_data)
            print(f"✅ Created dataset (sync): {created_dataset.id}")

            print("📋 Listing datasets (sync)...")
            datasets = real_sync_dataset_api.list(page_size=5)
            print(f"✅ Found {len(datasets.results)} datasets (sync)")

            dataset_ids = [d.id for d in datasets.results]
            assert created_dataset.id in dataset_ids

        except Exception as e:
            print(f"❌ Error in sync dataset operations: {e}")
            raise

        finally:
            # Cleanup
            if created_dataset:
                try:
                    real_sync_dataset_api.delete(created_dataset.id)
                    print("✅ Test dataset deleted (sync)")
                except Exception as cleanup_error:
                    print(f"⚠️ Warning: Could not delete test dataset: {cleanup_error}")


class TestKeywordsAIEvaluationWorkflowIntegration:
    """Test Keywords AI evaluation workflow with real API calls"""

    @pytest.mark.asyncio
    async def test_evaluation_discovery_real(
        self, real_dataset_api, real_evaluator_api, test_dataset_data
    ):
        """Test discovering evaluators and running evaluations with real API"""
        print("\n🔍 Testing real evaluation workflow...")

        created_dataset = None
        try:
            # 1. Create a test dataset
            print("📝 Creating dataset for evaluation...")
            created_dataset = await real_dataset_api.create(test_dataset_data)
            print(f"✅ Created dataset: {created_dataset.id}")

            # 2. List available evaluators
            print("📋 Discovering available evaluators...")
            evaluators = await real_evaluator_api.list(page_size=10)
            print(f"✅ Found {len(evaluators.results)} evaluators")

            if not evaluators.results:
                print("⚠️ No evaluators available, skipping evaluation test")
                return

            # 3. Try to run evaluation (this might fail if dataset has no logs)
            evaluator_slug = evaluators.results[0].slug
            print(f"🎯 Attempting to run evaluation with: {evaluator_slug}")

            try:
                eval_result = await real_dataset_api.run_dataset_evaluation(
                    created_dataset.id, [evaluator_slug]
                )
                print(f"✅ Evaluation started: {eval_result}")

                # 4. Try to list evaluation reports
                print("📊 Listing evaluation reports...")
                reports = await real_dataset_api.list_evaluation_reports(
                    created_dataset.id
                )
                print(f"✅ Found {len(reports.results)} evaluation reports")

            except Exception as eval_error:
                print(
                    f"⚠️ Evaluation may have failed (expected if dataset has no logs): {eval_error}"
                )
                # This is expected if the dataset doesn't have logs to evaluate

        except Exception as e:
            print(f"❌ Error in evaluation workflow: {e}")
            raise

        finally:
            # Cleanup
            if created_dataset:
                try:
                    await real_dataset_api.delete(created_dataset.id)
                    print("✅ Test dataset deleted")
                except Exception as cleanup_error:
                    print(f"⚠️ Warning: Could not delete test dataset: {cleanup_error}")


class TestKeywordsAIAPIErrorHandlingIntegration:
    """Test error handling with real Keywords AI API calls"""

    @pytest.mark.asyncio
    async def test_nonexistent_dataset_real(self, real_dataset_api):
        """Test handling of non-existent dataset with real API"""
        print("\n🔍 Testing real API error handling...")

        try:
            # Try to get a dataset that doesn't exist
            await real_dataset_api.get("nonexistent_dataset_123")
            pytest.fail("Expected an error for non-existent dataset")
        except Exception as e:
            print(
                f"✅ Correctly handled non-existent dataset error: {type(e).__name__}"
            )
            # This should raise an HTTP error (404, 400, etc.)
            assert (
                "error" in str(e).lower()
                or "not found" in str(e).lower()
                or "404" in str(e)
            )

    @pytest.mark.asyncio
    async def test_nonexistent_evaluator_real(self, real_evaluator_api):
        """Test handling of non-existent evaluator with real API"""
        print("\n🔍 Testing real evaluator error handling...")

        try:
            # Try to get an evaluator that doesn't exist
            await real_evaluator_api.get("nonexistent_evaluator_123")
            pytest.fail("Expected an error for non-existent evaluator")
        except Exception as e:
            print(
                f"✅ Correctly handled non-existent evaluator error: {type(e).__name__}"
            )
            # This should raise an HTTP error (404, 400, etc.)
            assert (
                "error" in str(e).lower()
                or "not found" in str(e).lower()
                or "404" in str(e)
            )


async def demo_workflow():
    """Demo workflow when running as script (not pytest)"""
    print("🚀 Keywords AI SDK Demo Workflow")
    print("=" * 50)
    
    # Setup
    api_key = os.getenv("KEYWORDSAI_API_KEY")
    base_url = os.getenv("KEYWORDSAI_BASE_URL", "http://localhost:8000")
    
    if not api_key:
        print("❌ KEYWORDSAI_API_KEY not found in environment")
        print("   Please set your API key in .env file")
        return
    
    print(f"🔗 Using API: {base_url}")
    print()
    
    # Initialize clients
    dataset_api = DatasetAPI(api_key=api_key, base_url=base_url)
    evaluator_api = EvaluatorAPI(api_key=api_key, base_url=base_url)
    
    created_dataset = None
    
    try:
        # Demo: List evaluators
        print("🔍 Demo: Listing available evaluators...")
        evaluators = await evaluator_api.alist(page_size=5)
        print(f"   ✅ Found {len(evaluators.results)} evaluators")
        
        if evaluators.results:
            for i, evaluator in enumerate(evaluators.results[:3], 1):
                print(f"   {i}. {evaluator.name} (slug: {evaluator.slug})")
        print()
        
        # Demo: Create dataset
        print("📝 Demo: Creating a test dataset...")
        from datetime import datetime, timedelta
        now = datetime.utcnow()
        week_ago = now - timedelta(days=7)
        
        dataset_data = DatasetCreate(
            name=f"DEMO_DATASET_{int(now.timestamp())}",
            description="Demo dataset created by SDK",
            type="sampling",
            sampling=5,
            start_time=week_ago.isoformat() + "Z",
            end_time=now.isoformat() + "Z",
        )
        
        created_dataset = await dataset_api.acreate(dataset_data)
        print(f"   ✅ Created: {created_dataset.name}")
        print(f"   🆔 ID: {created_dataset.id}")
        print()
        
        # Demo: List datasets
        print("📋 Demo: Listing datasets...")
        datasets = await dataset_api.alist(page_size=5)
        print(f"   ✅ Found {len(datasets.results)} datasets")
        for i, ds in enumerate(datasets.results[:3], 1):
            print(f"   {i}. {ds.name}")
        print()
        
        # Demo: Update dataset
        print("✏️  Demo: Updating dataset...")
        update_data = DatasetUpdate(name=f"{dataset_data.name}_UPDATED")
        updated_dataset = await dataset_api.aupdate(created_dataset.id, update_data)
        print(f"   ✅ Updated name: {updated_dataset.name}")
        print()
        
        print("🎉 Demo completed successfully!")
        print("\n💡 To run the full test suite instead:")
        print("   python -m pytest tests/test_keywords_ai_api_integration.py -v -s")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        # Cleanup
        if created_dataset:
            try:
                print("\n🗑️  Cleaning up demo dataset...")
                await dataset_api.adelete(created_dataset.id)
                print("   ✅ Demo dataset deleted")
            except Exception as cleanup_error:
                print(f"   ⚠️  Could not delete dataset: {cleanup_error}")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        # Run pytest mode
        print("🧪 Running Real API Integration Tests...")
        print("=" * 60)
        pytest.main([__file__, "-v", "-s", "--tb=short"])
    else:
        # Run demo mode
        asyncio.run(demo_workflow())
