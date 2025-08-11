#!/usr/bin/env node
/**
 * Keywords AI Dataset Workflow Example
 *
 * This example demonstrates the complete dataset workflow:
 * 1. List available logs
 * 2. Create a new dataset
 * 3. Add logs to the dataset
 * 4. List datasets
 * 5. Update dataset
 * 6. Run evaluation on dataset
 * 7. Get evaluation results
 *
 * Usage:
 *     npm run build && node dist/examples/dataset-workflow-example.js
 *     or
 *     npx tsx examples/dataset-workflow-example.ts
 *
 * Environment variables required:
 * - KEYWORDSAI_API_KEY
 * - KEYWORDSAI_BASE_URL (optional, defaults to http://localhost:8000)
 */

import { config } from 'dotenv';
import {
  DatasetAPI,
  EvaluatorAPI,
  type DatasetCreate,
  type DatasetUpdate,
  type LogManagementRequest,
} from '../src/index.js';

// Load environment variables with override
config({ override: true });

async function main() {
  // Setup
  const apiKey = process.env.KEYWORDSAI_API_KEY;
  const baseUrl = process.env.KEYWORDSAI_BASE_URL || 'http://localhost:8000';

  if (!apiKey) {
    console.log('❌ KEYWORDSAI_API_KEY not found in environment');
    console.log('   Please set your API key in .env file');
    return;
  }

  console.log('🚀 Keywords AI Dataset Workflow Example');
  console.log('='.repeat(50));
  console.log(`🔗 Using API: ${baseUrl}`);
  console.log();

  // Initialize clients
  const datasetApi = new DatasetAPI({ apiKey, baseUrl });
  const evaluatorApi = new EvaluatorAPI({ apiKey, baseUrl });

  let createdDataset: any = null;

  try {
    // Step 1: List available logs for dataset creation
    console.log('📋 Step 1: Listing available logs...');
    const weekAgo = new Date();
    weekAgo.setDate(weekAgo.getDate() - 7);
    const now = new Date();

    // For demo purposes, we'll simulate having logs
    // In real usage, you'd get logs from the logs API
    const logsResponse = {
      results: [
        { id: 'log-1' },
        { id: 'log-2' },
        { id: 'log-3' }
      ]
    };

    console.log(`   ✅ Found ${logsResponse.results?.length || 0} logs`);
    let logIds: string[] = [];
    if (logsResponse.results && logsResponse.results.length > 0) {
      logIds = logsResponse.results.slice(0, 5).map((log: any) => log.id);
      console.log(`   📄 Sample log IDs: ${logIds.slice(0, 3).join(', ')}...`);
    } else {
      console.log('   ⚠️  No logs found in the specified time range');
    }
    console.log();

    // Step 2: Create a new dataset
    console.log('📝 Step 2: Creating a new dataset...');
    // Note: You can also use a simple dictionary instead of DatasetCreate!
    // See examples/flexible-input-example.ts for dictionary-based usage
    const datasetData: DatasetCreate = {
      name: `EXAMPLE_DATASET_${Math.floor(now.getTime() / 1000)}`,
      description: 'Example dataset created by SDK workflow',
      type: 'sampling',
      sampling: 10,
      start_time: weekAgo.toISOString(),
      end_time: now.toISOString()
    };

    createdDataset = await datasetApi.create(datasetData);
    console.log(`   ✅ Created dataset: ${createdDataset.name}`);
    console.log(`   🆔 Dataset ID: ${createdDataset.id}`);
    console.log(`   📊 Type: ${createdDataset.type}, Sampling: ${createdDataset.sampling || 'N/A'}`);
    console.log();

    // Step 3: Add logs to dataset (if we have logs)
    if (logIds.length > 0) {
      console.log('➕ Step 3: Adding logs to dataset...');
      const logRequest: LogManagementRequest = {
        start_time: weekAgo.toISOString().replace('T', ' ').slice(0, -5),
        end_time: now.toISOString().replace('T', ' ').slice(0, -5),
        filters: {
          id: {
            value: logIds,
            operator: 'in'
          }
        }
      };

      const addResult = await datasetApi.addLogsToDataset(createdDataset.id, logRequest);
      console.log(`   ✅ ${addResult.message || 'Logs added'}`);
      if (addResult.count !== undefined) {
        console.log(`   📊 Logs processed: ${addResult.count}`);
      }
      console.log();
    } else {
      console.log('⏭️  Step 3: Skipping log addition (no logs available)');
      console.log();
    }

    // Step 4: List all datasets
    console.log('📋 Step 4: Listing all datasets...');
    const datasets = await datasetApi.list({ pageSize: 5 });
    console.log(`   ✅ Found ${datasets.results.length} datasets`);
    for (let i = 0; i < Math.min(3, datasets.results.length); i++) {
      const ds = datasets.results[i];
      console.log(`   ${i + 1}. ${ds.name} (ID: ${ds.id})`);
    }
    console.log();

    // Step 5: Update the dataset
    console.log('✏️  Step 5: Updating dataset name...');
    const updateData: DatasetUpdate = { 
      name: `${datasetData.name}_UPDATED` 
    };
    const updatedDataset = await datasetApi.update(createdDataset.id, updateData);
    console.log(`   ✅ Updated name: ${updatedDataset.name}`);
    console.log();

    // Step 6: List available evaluators
    console.log('🔍 Step 6: Discovering available evaluators...');
    const evaluators = await evaluatorApi.list({ pageSize: 5 });
    console.log(`   ✅ Found ${evaluators.results.length} evaluators`);

    if (evaluators.results.length > 0) {
      for (let i = 0; i < Math.min(3, evaluators.results.length); i++) {
        const evaluator = evaluators.results[i];
        console.log(`   ${i + 1}. ${evaluator.name} (slug: ${evaluator.slug})`);
      }
      console.log();

      // Step 7: Run evaluation on dataset
      console.log('🎯 Step 7: Running evaluation on dataset...');
      const evaluatorSlug = evaluators.results[0].slug;
      console.log(`   🔧 Using evaluator: ${evaluatorSlug}`);

      try {
        const evalResult = await datasetApi.runDatasetEvaluation(
          createdDataset.id,
          [evaluatorSlug]
        );
        console.log(`   ✅ ${evalResult.message || 'Evaluation started'}`);
        console.log();

        // Step 8: Check evaluation results
        console.log('📊 Step 8: Checking evaluation results...');
        const reports = await datasetApi.listEvaluationReports(createdDataset.id);
        console.log(`   ✅ Found ${reports.results.length} evaluation reports`);

        if (reports.results.length > 0) {
          for (let i = 0; i < Math.min(2, reports.results.length); i++) {
            const report = reports.results[i];
            console.log(`   ${i + 1}. Report ID: ${report.id}`);
            if (report.status) {
              console.log(`      Status: ${report.status}`);
            }
          }
        }
        console.log();

      } catch (evalError) {
        console.log(`   ⚠️  Evaluation failed (may be expected if dataset has no logs): ${evalError}`);
        console.log();
      }
    } else {
      console.log('   ⚠️  No evaluators available');
      console.log();
    }

    // Step 9: Get dataset details
    console.log('📖 Step 9: Retrieving final dataset details...');
    const finalDataset = await datasetApi.get(createdDataset.id);
    console.log(`   ✅ Dataset: ${finalDataset.name}`);
    console.log(`   📅 Created: ${finalDataset.created_at || 'N/A'}`);
    console.log(`   📝 Description: ${finalDataset.description}`);
    console.log();

    console.log('🎉 Workflow completed successfully!');

  } catch (error) {
    console.log(`❌ Error in workflow: ${error}`);
    if (error instanceof Error) {
      console.error(error.stack);
    }

  } finally {
    // Cleanup
    if (createdDataset) {
      try {
        console.log('\n🗑️  Cleaning up...');
        await datasetApi.delete(createdDataset.id);
        console.log('   ✅ Test dataset deleted');
      } catch (cleanupError) {
        console.log(`   ⚠️  Could not delete dataset: ${cleanupError}`);
      }
    }
  }
}

if (import.meta.url === `file://${process.argv[1]}`) {
  main().catch(console.error);
}
