#!/usr/bin/env node
/**
 * Simple Evaluator Example
 *
 * This example shows how to:
 * 1. List available evaluators
 * 2. Get details of a specific evaluator
 * 3. Filter evaluators by type
 *
 * Usage:
 *     npm run build && node dist/examples/simple-evaluator-example.js
 *     or
 *     npx tsx examples/simple-evaluator-example.ts
 *
 * Environment variables required:
 * - KEYWORDSAI_API_KEY
 * - KEYWORDSAI_BASE_URL (optional)
 */

import { config } from 'dotenv';
import { EvaluatorAPI } from '../src/index.js';

// Load environment variables with override
config({ override: true });

async function main() {
  console.log('🔍 Keywords AI Evaluators Example');
  console.log('='.repeat(40));

  const apiKey = process.env.KEYWORDSAI_API_KEY;
  const baseUrl = process.env.KEYWORDSAI_BASE_URL || 'http://localhost:8000';

  if (!apiKey) {
    console.log('❌ KEYWORDSAI_API_KEY not found in environment');
    return;
  }

  console.log(`🔗 Using API: ${baseUrl}`);
  console.log();

  const evaluatorApi = new EvaluatorAPI({ apiKey, baseUrl });

  try {
    // List all evaluators
    console.log('📋 Listing all available evaluators...');
    const evaluators = await evaluatorApi.list({ pageSize: 10 });

    console.log(`✅ Found ${evaluators.results.length} evaluators:`);
    console.log();

    for (let i = 0; i < evaluators.results.length; i++) {
      const evaluator = evaluators.results[i];
      console.log(`${(i + 1).toString().padStart(2)}. ${evaluator.name}`);
      console.log(`     Slug: ${evaluator.slug}`);
      console.log(`     ID: ${evaluator.id}`);
      if (evaluator.description) {
        console.log(`     Description: ${evaluator.description}`);
      }
      console.log();
    }

    if (evaluators.results.length > 0) {
      // Get details of first evaluator
      const firstEvaluator = evaluators.results[0];
      console.log(`🔍 Getting details for: ${firstEvaluator.name}`);

      const detailedEvaluator = await evaluatorApi.get(firstEvaluator.id);
      console.log(`✅ Retrieved: ${detailedEvaluator.name}`);
      console.log(`   Slug: ${detailedEvaluator.slug}`);

      // Print all available attributes
      console.log('   Available attributes:');
      for (const [key, value] of Object.entries(detailedEvaluator)) {
        if (typeof value !== 'function') {
          console.log(`     ${key}: ${value}`);
        }
      }
    }

  } catch (error) {
    console.log(`❌ Error: ${error}`);
    if (error instanceof Error) {
      console.error(error.stack);
    }
  }
}

if (import.meta.url === `file://${process.argv[1]}`) {
  main().catch(console.error);
}
