#!/usr/bin/env node
/**
 * Experiment API Workflow Example
 *
 * This example demonstrates how to use the Respan Experiment API to:
 * 1. Create an experiment with columns and rows
 * 2. Add more rows and columns
 * 3. Run the experiment
 * 4. Run evaluations
 *
 * Environment variables required:
 * - RESPAN_API_KEY
 * - RESPAN_BASE_URL (optional, defaults to production)
 *
 * Usage:
 *     npm run build && node dist/examples/experiment-workflow-example.js
 *     or
 *     npx tsx examples/experiment-workflow-example.ts
 */

import { config } from 'dotenv';
import {
  ExperimentAPI,
  type ExperimentCreate,
  type ExperimentColumnType,
  type ExperimentRowType,
  type AddExperimentRowsRequest,
  type AddExperimentColumnsRequest,
  type RunExperimentRequest,
  type RunExperimentEvalsRequest,
  type ExperimentUpdate,
} from '../src/index.js';

// Load environment variables with override
config({ override: true });

async function main() {
  // Initialize the API client
  const apiKey = process.env.RESPAN_API_KEY;
  const baseUrl = process.env.RESPAN_BASE_URL; // Optional

  if (!apiKey) {
    console.log('❌ RESPAN_API_KEY environment variable is required');
    return;
  }

  const client = new ExperimentAPI({ apiKey, baseUrl });
  console.log('✅ Experiment API client initialized');

  // Generate unique experiment name
  const timestamp = new Date().toISOString().replace(/[-:.]/g, '').slice(0, 15);
  const experimentName = `SDK_Example_Experiment_${timestamp}`;

  let experiment: any = null;

  try {
    // Step 1: Create an experiment with initial columns and rows
    console.log('\n🔬 Step 1: Creating experiment...');

    // Note: You can also use a simple dictionary instead of ExperimentColumnType!
    // See examples/flexible-input-example.ts for dictionary-based usage
    const initialColumn: ExperimentColumnType = {
      model: 'gpt-3.5-turbo',
      name: 'Helpful Assistant',
      temperature: 0.7,
      max_completion_tokens: 200,
      top_p: 1.0,
      frequency_penalty: 0.0,
      presence_penalty: 0.0,
      prompt_messages: [
        {
          role: 'system',
          content: 'You are a helpful assistant. Answer questions clearly and concisely.'
        },
        {
          role: 'user',
          content: '{{question}}'
        }
      ],
      tools: [],
      tool_choice: 'auto',
      response_format: { type: 'text' }
    };

    const initialRow: ExperimentRowType = {
      input: { question: 'What is artificial intelligence?' },
      ideal_output: 'AI is the simulation of human intelligence in machines.'
    };

    const experimentData: ExperimentCreate = {
      name: experimentName,
      description: 'Example experiment demonstrating SDK capabilities',
      columns: [initialColumn],
      rows: [initialRow]
    };

    experiment = await client.create(experimentData);
    console.log(`✅ Created experiment: ${experiment.name} (ID: ${experiment.id})`);

    // Step 2: Add more test cases (rows)
    console.log('\n📝 Step 2: Adding more test cases...');

    const newRows: ExperimentRowType[] = [
      {
        input: { question: 'What is machine learning?' },
        ideal_output: 'ML is a subset of AI that learns from data.'
      },
      {
        input: { question: 'Explain neural networks briefly.' },
        ideal_output: 'Neural networks are computing systems inspired by biological neural networks.'
      },
      {
        input: { question: 'What is the difference between AI and ML?' }
        // No ideal_output for this one
      }
    ];

    const addRowsRequest: AddExperimentRowsRequest = { rows: newRows };
    await client.addRows(experiment.id, addRowsRequest);
    console.log(`✅ Added ${newRows.length} test cases`);

    // Step 3: Add another model configuration (column)
    console.log('\n🤖 Step 3: Adding another model configuration...');

    const newColumn: ExperimentColumnType = {
      model: 'gpt-4',
      name: 'Expert Assistant',
      temperature: 0.3, // Lower temperature for more focused responses
      max_completion_tokens: 250,
      top_p: 1.0,
      frequency_penalty: 0.0,
      presence_penalty: 0.0,
      prompt_messages: [
        {
          role: 'system',
          content: 'You are an expert technical assistant. Provide accurate, detailed explanations.'
        },
        {
          role: 'user',
          content: '{{question}}'
        }
      ],
      tools: [],
      tool_choice: 'auto',
      response_format: { type: 'text' }
    };

    const addColumnsRequest: AddExperimentColumnsRequest = { columns: [newColumn] };
    await client.addColumns(experiment.id, addColumnsRequest);
    console.log('✅ Added GPT-4 configuration');

    // Step 4: Update experiment metadata
    console.log('\n✏️  Step 4: Updating experiment metadata...');

    const updateData: ExperimentUpdate = {
      name: `${experimentName}_Updated`,
      description: 'Updated experiment description with more details about the SDK workflow'
    };
    const updatedExperiment = await client.update(experiment.id, updateData);
    console.log(`✅ Updated experiment name to: ${updatedExperiment.name}`);

    // Step 5: Check the updated experiment
    console.log('\n🔍 Step 5: Checking experiment status...');

    const finalExperiment = await client.get(experiment.id);
    console.log(`📊 Experiment now has:`);
    console.log(`   - ${finalExperiment.columns?.length || 0} columns (model configurations)`);
    console.log(`   - ${finalExperiment.rows?.length || 0} rows (test cases)`);
    console.log(`   - Status: ${finalExperiment.status}`);
    console.log(`   - Name: ${finalExperiment.name}`);
    console.log(`   - Description: ${finalExperiment.description}`);

    // Step 6: Run the experiment (optional - may take time)
    console.log('\n🚀 Step 6: Running experiment...');
    console.log('⚠️  Note: This will make API calls to generate responses and may take time');

    const runResult = await client.runExperiment(experiment.id);
    console.log('✅ Experiment run initiated');
    console.log(`📋 Run status: ${JSON.stringify(runResult)}`);

    // Step 7: Run evaluations (optional)
    console.log('\n📊 Step 7: Running evaluations...');
    console.log('⚠️  Note: This requires the experiment to have outputs');

    try {
      const evalsRequest: RunExperimentEvalsRequest = {
        evaluator_slugs: ['is_english'] // Basic evaluator
      };
      const evalResult = await client.runExperimentEvals(experiment.id, evalsRequest);
      console.log('✅ Evaluations initiated');
      console.log(`📊 Evaluation status: ${JSON.stringify(evalResult)}`);
    } catch (e) {
      console.log(`⚠️  Evaluation skipped: ${e}`);
    }

    // Step 8: List all experiments
    console.log('\n📋 Step 8: Listing experiments...');

    const experiments = await client.list({ pageSize: 5 });
    console.log(`📊 Found ${experiments.total} total experiments`);
    console.log('Recent experiments:');
    for (const exp of experiments.experiments.slice(0, 3)) {
      console.log(`   - ${exp.name} (ID: ${exp.id})`);
    }

    console.log(`\n✅ Workflow completed successfully!`);
    console.log(`🔬 Experiment '${experiment.name}' is ready for analysis`);
    console.log(`🌐 You can view it in the Respan dashboard`);

  } catch (error) {
    console.log(`❌ Error during workflow: ${error}`);
    if (error instanceof Error) {
      console.error(error.stack);
    }
    return;

  } finally {
    // Optional: Clean up the test experiment
    // Uncomment the following lines if you want to auto-delete the test experiment
    // if (experiment) {
    //   console.log(`\n🧹 Cleaning up test experiment...`);
    //   await client.delete(experiment.id);
    //   console.log('✅ Test experiment deleted');
    // }
  }
}

async function syncExample() {
  console.log('🔄 Running synchronous example...');

  const apiKey = process.env.RESPAN_API_KEY;
  const baseUrl = process.env.RESPAN_BASE_URL;

  if (!apiKey) {
    console.log('❌ RESPAN_API_KEY environment variable is required');
    return;
  }

  const client = new ExperimentAPI({ apiKey, baseUrl });

  // Simple synchronous workflow
  const timestamp = new Date().toISOString().replace(/[-:.]/g, '').slice(0, 15);

  const column: ExperimentColumnType = {
    model: 'gpt-3.5-turbo',
    name: 'Sync Test Column',
    temperature: 0.5,
    max_completion_tokens: 150,
    top_p: 1.0,
    frequency_penalty: 0.0,
    presence_penalty: 0.0,
    prompt_messages: [
      { role: 'system', content: 'You are a helpful assistant.' },
      { role: 'user', content: '{{input}}' }
    ],
    tools: [],
    tool_choice: 'auto',
    response_format: { type: 'text' }
  };

  const row: ExperimentRowType = {
    input: { input: 'Hello, how are you?' }
  };

  const experimentData: ExperimentCreate = {
    name: `SDK_Sync_Example_${timestamp}`,
    description: 'Synchronous SDK example',
    columns: [column],
    rows: [row]
  };

  try {
    // Create experiment synchronously
    const experiment = await client.create(experimentData);
    console.log(`✅ Sync: Created experiment ${experiment.name}`);

    // List experiments synchronously
    const experiments = await client.list({ pageSize: 3 });
    console.log(`✅ Sync: Listed ${experiments.experiments.length} experiments`);

    // Get experiment synchronously
    if (experiment?.id) {
      const retrieved = await client.get(experiment.id);
      console.log(`✅ Sync: Retrieved experiment ${retrieved.name}`);
    }

    console.log('✅ Synchronous workflow completed!');

  } catch (error) {
    console.log(`❌ Sync error: ${error}`);
  }
}

if (import.meta.url === `file://${process.argv[1]}`) {
  console.log('🚀 Respan Experiment API Example');
  console.log('=====================================');

  // Run async example
  console.log('\n1️⃣  Running asynchronous workflow...');
  main().then(async () => {
    console.log('\n' + '='.repeat(50));

    // Run sync example
    console.log('\n2️⃣  Running synchronous workflow...');
    return await syncExample();
  }).then(() => {
    console.log('\n🎉 All examples completed!');
    console.log('\n💡 Tips:');
    console.log('   - Check the Respan dashboard to see your experiments');
    console.log('   - Use the experiment results to compare model performance');
    console.log('   - Run evaluations to get automated scoring');
    console.log('   - Export results for further analysis');
  }).catch(console.error);
}
