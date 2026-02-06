#!/usr/bin/env node
/**
 * Example demonstrating flexible input options for Keywords AI TypeScript SDK
 *
 * This example shows how you can use either plain objects or strongly-typed interfaces
 * as input to all API methods. This makes the SDK much more user-friendly
 * by eliminating the need to import and construct complex nested types.
 *
 * Usage:
 *     npm run build && node dist/examples/flexible-input-example.js
 *     or
 *     npx tsx examples/flexible-input-example.ts
 */

import { config } from 'dotenv';
import {
  ExperimentAPI,
  DatasetAPI,
  LogAPI,
  // You can still import the types if you want to use them
  type ExperimentCreate,
  type DatasetCreate,
} from '../src/index.js';

// Load environment variables with override
config({ override: true });

async function main() {
  // Initialize clients
  const apiKey = process.env.KEYWORDSAI_API_KEY || 'your-api-key';
  const baseUrl = process.env.KEYWORDSAI_BASE_URL;

  const experimentClient = new ExperimentAPI({ apiKey, baseUrl });
  const datasetClient = new DatasetAPI({ apiKey, baseUrl });
  const logClient = new LogAPI({ apiKey, baseUrl });

  console.log('=== EXPERIMENTS API - Flexible Input Examples ===\n');

  // Option 1: Using plain objects (much simpler!)
  console.log('1. Creating experiment with plain object input:');
  const experimentDict = {
    name: 'My Simple Experiment',
    description: 'Created using a simple object',
    columns: [
      {
        model: 'gpt-3.5-turbo',
        name: 'Version A',
        temperature: 0.7,
        max_completion_tokens: 256,
        top_p: 1.0,
        frequency_penalty: 0.0,
        presence_penalty: 0.0,
        prompt_messages: [
          { role: 'system', content: 'You are a helpful assistant.' },
          { role: 'user', content: '{{user_input}}' }
        ],
        tools: [],
        tool_choice: 'auto',
        response_format: { type: 'text' }
      }
    ],
    rows: [
      {
        input: { user_input: 'What is the weather like?' }
      }
    ]
  };

  try {
    // This works with a simple object!
    const experiment = await experimentClient.create(experimentDict as ExperimentCreate);
    console.log(`✓ Created experiment: ${experiment.name}`);
  } catch (error) {
    console.log(`✗ Error: ${error}`);
  }

  // Option 2: Using typed interfaces (still supported)
  console.log('\n2. Creating experiment with typed interface:');
  try {
    const experimentTyped: ExperimentCreate = {
      name: 'My Typed Experiment',
      description: 'Created using TypeScript interface',
      columns: [
        {
          model: 'gpt-4',
          name: 'Version B',
          temperature: 0.3,
          max_completion_tokens: 200,
          top_p: 1.0,
          frequency_penalty: 0.0,
          presence_penalty: 0.0,
          prompt_messages: [
            { role: 'system', content: 'You are a formal assistant.' }
          ],
          tools: [],
          tool_choice: 'auto',
          response_format: { type: 'text' }
        }
      ],
      rows: [
        {
          input: { user_input: 'Explain quantum computing' }
        }
      ]
    };

    const experiment = await experimentClient.create(experimentTyped);
    console.log(`✓ Created experiment: ${experiment.name}`);
  } catch (error) {
    console.log(`✗ Error: ${error}`);
  }

  console.log('\n=== DATASETS API - Flexible Input Examples ===\n');

  // Option 1: Using plain objects for dataset creation
  console.log('1. Creating dataset with plain object input:');
  const datasetDict = {
    name: 'My Simple Dataset',
    description: 'Created using a simple object',
    type: 'sampling',
    sampling: 100,
    start_time: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString(), // 7 days ago
    end_time: new Date().toISOString(),
    initial_log_filters: {
      status: { value: 'success', operator: 'equals' }
    }
  };

  try {
    const dataset = await datasetClient.create(datasetDict as DatasetCreate);
    console.log(`✓ Created dataset: ${dataset.name}`);
  } catch (error) {
    console.log(`✗ Error: ${error}`);
  }

  // Option 2: Using typed interface
  console.log('\n2. Creating dataset with typed interface:');
  try {
    const datasetTyped: DatasetCreate = {
      name: 'My Typed Dataset',
      description: 'Created using TypeScript interface',
      type: 'sampling',
      sampling: 200,
      start_time: new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString(), // 24 hours ago
      end_time: new Date().toISOString(),
      initial_log_filters: {
        model: { value: 'gpt-4', operator: 'equals' },
        status: { value: 'success', operator: 'equals' }
      }
    };

    const dataset = await datasetClient.create(datasetTyped);
    console.log(`✓ Created dataset: ${dataset.name}`);
  } catch (error) {
    console.log(`✗ Error: ${error}`);
  }

  console.log('\n=== LOGS API - Flexible Input Examples ===\n');

  // Option 1: Using plain objects for log creation
  console.log('1. Creating log with plain object input:');
  const logDict = {
    model: 'gpt-3.5-turbo',
    input: 'Hello, how can I help you today?',
    output: 'I am here to assist you with any questions you might have!',
    status_code: 200,
    custom_identifier: 'example_log_001'
  };

  try {
    const log = await logClient.create(logDict);
    console.log(`✓ Created log successfully`);
  } catch (error) {
    console.log(`✗ Error: ${error}`);
  }

  // Option 2: More complex log with additional fields
  console.log('\n2. Creating log with additional fields:');
  const complexLogDict = {
    model: 'gpt-4',
    input: 'What is machine learning?',
    output: 'Machine learning is a subset of artificial intelligence...',
    status_code: 200,
    prompt_tokens: 15,
    completion_tokens: 45,
    total_tokens: 60,
    latency: 1250,
    cost: 0.002,
    custom_identifier: 'ml_explanation_001',
    user_id: 'user_123',
    timestamp: new Date().toISOString()
  };

  try {
    const log = await logClient.create(complexLogDict);
    console.log(`✓ Created complex log successfully`);
  } catch (error) {
    console.log(`✗ Error: ${error}`);
  }

  console.log('\n=== ROW AND COLUMN MANAGEMENT - Flexible Examples ===\n');

  // Adding rows with plain objects
  console.log('1. Adding experiment rows with plain objects:');
  try {
    const experiments = await experimentClient.list({ pageSize: 1 });
    if (experiments.experiments.length > 0) {
      const experimentId = experiments.experiments[0].id;
      if (experimentId) {
        // Add rows using plain objects
        const newRowsDict = {
          rows: [
            {
              input: { question: 'What is TypeScript?' },
              ideal_output: 'TypeScript is a strongly typed programming language...'
            },
            {
              input: { question: 'Explain async/await' }
              // No ideal output for this one
            }
          ]
        };

        await experimentClient.addRows(experimentId, newRowsDict);
        console.log(`✓ Added rows using plain objects`);
      }
    }
  } catch (error) {
    console.log(`✗ Error: ${error}`);
  }

  // Adding columns with plain objects
  console.log('\n2. Adding experiment columns with plain objects:');
  try {
    const experiments = await experimentClient.list({ pageSize: 1 });
    if (experiments.experiments.length > 0) {
      const experimentId = experiments.experiments[0].id;
      if (experimentId) {
        // Add column using plain object
        const newColumnDict = {
          columns: [
            {
              model: 'gpt-4-turbo',
              name: 'Turbo Assistant',
              temperature: 0.5,
              max_completion_tokens: 300,
              top_p: 1.0,
              frequency_penalty: 0.0,
              presence_penalty: 0.0,
              prompt_messages: [
                { role: 'system', content: 'You are a fast and efficient assistant.' },
                { role: 'user', content: '{{question}}' }
              ],
              tools: [],
              tool_choice: 'auto',
              response_format: { type: 'text' }
            }
          ]
        };

        await experimentClient.addColumns(experimentId, newColumnDict);
        console.log(`✓ Added column using plain object`);
      }
    }
  } catch (error) {
    console.log(`✗ Error: ${error}`);
  }

  console.log('\n=== BENEFITS OF FLEXIBLE INPUT ===\n');
  console.log('✅ No need to import complex nested types');
  console.log('✅ Simpler code with plain JavaScript objects');
  console.log('✅ Still get TypeScript type checking when desired');
  console.log('✅ Easier for beginners to get started');
  console.log('✅ More flexible for dynamic use cases');
  console.log('✅ Compatible with JSON configurations');
  console.log();

  console.log('💡 Tips:');
  console.log('   - Use plain objects for simple, one-off operations');
  console.log('   - Use typed interfaces for complex, reusable code');
  console.log('   - Mix and match approaches as needed');
  console.log('   - The SDK validates input regardless of approach');
  console.log();

  console.log('🎉 Flexible input examples completed!');
}

if (import.meta.url === `file://${process.argv[1]}`) {
  main().catch(console.error);
}
