#!/usr/bin/env node
/**
 * Keywords AI SDK Structure Demo
 *
 * This example shows the SDK structure and how to initialize clients
 * without making actual API calls.
 *
 * Usage:
 *     npm run build && node dist/examples/sdk-structure-demo.js
 *     or
 *     npx tsx examples/sdk-structure-demo.ts
 */

import { config } from 'dotenv';
import {
  DatasetAPI,
  ExperimentAPI,
  EvaluatorAPI,
  LogAPI,
} from '../src/index.js';

// Load environment variables with override
config({ override: true });

function main() {
  console.log('🏗️  Keywords AI SDK Structure Demo');
  console.log('='.repeat(50));

  // 1. Show SDK structure
  console.log('📦 Available API Clients:');
  console.log('   📊 DatasetAPI - Manage datasets');
  console.log('   🧪 ExperimentAPI - Manage experiments');
  console.log('   🔍 EvaluatorAPI - Work with evaluators');
  console.log('   📝 LogAPI - Manage logs');
  console.log();

  // 2. Show initialization
  console.log('🔧 Client Initialization:');
  const apiKey = process.env.KEYWORDSAI_API_KEY || 'your-api-key-here';
  const baseUrl = process.env.KEYWORDSAI_BASE_URL || 'http://localhost:8000';

  console.log(`   🔑 API Key: ${apiKey.length > 10 ? apiKey.slice(0, 10) + '...' : apiKey}`);
  console.log(`   🌐 Base URL: ${baseUrl}`);
  console.log();

  // Initialize clients (no API calls yet)
  console.log('🚀 Initializing clients...');
  const datasetApi = new DatasetAPI({ apiKey, baseUrl });
  const experimentApi = new ExperimentAPI({ apiKey, baseUrl });
  const evaluatorApi = new EvaluatorAPI({ apiKey, baseUrl });
  const logApi = new LogAPI({ apiKey, baseUrl });

  console.log('   ✅ DatasetAPI initialized');
  console.log('   ✅ ExperimentAPI initialized');
  console.log('   ✅ EvaluatorAPI initialized');
  console.log('   ✅ LogAPI initialized');
  console.log();

  // 3. Show available methods
  console.log('📋 Available Dataset Methods:');
  const datasetMethods = Object.getOwnPropertyNames(Object.getPrototypeOf(datasetApi))
    .filter(method => !method.startsWith('_') && typeof datasetApi[method as keyof typeof datasetApi] === 'function')
    .sort();
  
  for (const method of datasetMethods) {
    console.log(`   • ${method}()`);
  }
  console.log();

  console.log('📋 Available Evaluator Methods:');
  const evaluatorMethods = Object.getOwnPropertyNames(Object.getPrototypeOf(evaluatorApi))
    .filter(method => !method.startsWith('_') && typeof evaluatorApi[method as keyof typeof evaluatorApi] === 'function')
    .sort();
  
  for (const method of evaluatorMethods) {
    console.log(`   • ${method}()`);
  }
  console.log();

  // 4. Show data types
  console.log('📝 Available Data Types:');
  console.log('   📊 Dataset Types:');
  console.log('      • DatasetCreate - For creating new datasets');
  console.log('      • DatasetUpdate - For updating existing datasets');
  console.log('      • LogManagementRequest - For managing logs in datasets');
  console.log();
  console.log('   🧪 Experiment Types:');
  console.log('      • ExperimentCreate - For creating new experiments');
  console.log('      • ExperimentUpdate - For updating existing experiments');
  console.log('      • ExperimentColumnType - For experiment columns');
  console.log('      • ExperimentRowType - For experiment rows');
  console.log();
  console.log('   🔍 Evaluator Types:');
  console.log('      • Evaluator - Individual evaluator model');
  console.log('      • EvaluatorList - List of evaluators with pagination');
  console.log();
  console.log('   📝 Log Types:');
  console.log('      • KeywordsAILogParams - For creating logs');
  console.log('      • KeywordsAIFullLogParams - Full log data');
  console.log('      • LogList - List of logs with pagination');
  console.log();

  // 5. Usage examples
  console.log('💡 Basic Usage Examples:');
  console.log();
  console.log('   // Create a dataset');
  console.log('   const dataset = await datasetApi.create({');
  console.log('     name: "My Dataset",');
  console.log('     description: "Test dataset",');
  console.log('     type: "sampling"');
  console.log('   });');
  console.log();
  console.log('   // List evaluators');
  console.log('   const evaluators = await evaluatorApi.list();');
  console.log();
  console.log('   // Create a log');
  console.log('   const log = await logApi.create({');
  console.log('     model: "gpt-4",');
  console.log('     input: "Hello world",');
  console.log('     output: "Hi there!"');
  console.log('   });');
  console.log();

  console.log('🎯 Next Steps:');
  console.log('   1. Set KEYWORDSAI_API_KEY environment variable');
  console.log('   2. Run examples: npm run example:simple-evaluator');
  console.log('   3. Check out the dataset-workflow example');
  console.log('   4. Explore the experiment-workflow example');
  console.log();
  console.log('✅ SDK structure demo completed!');
}

if (import.meta.url === `file://${process.argv[1]}`) {
  main();
}
