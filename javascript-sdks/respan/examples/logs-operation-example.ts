#!/usr/bin/env node
/**
 * Simple Logs Operation Example
 *
 * This example shows basic log operations:
 * - List available logs
 * - Simple log API usage
 *
 * Usage:
 *     npm run build && node dist/examples/logs-operation-example.js
 *     or
 *     npx tsx examples/logs-operation-example.ts
 *
 * Environment variables required:
 * - KEYWORDSAI_API_KEY
 * - KEYWORDSAI_BASE_URL (optional)
 */

import { config } from 'dotenv';
import { LogAPI } from '../src/index.js';

// Load environment variables with override
config({ override: true });

async function main() {
  const apiKey = process.env.KEYWORDSAI_API_KEY;
  const baseUrl = process.env.KEYWORDSAI_BASE_URL;

  if (!apiKey) {
    console.log('❌ KEYWORDSAI_API_KEY not found in environment');
    return;
  }

  const logApiClient = new LogAPI({ apiKey, baseUrl });

  try {
    const logList = await logApiClient.list();
    console.log(logList);
  } catch (error) {
    console.error('❌ Error:', error);
  }
}

if (import.meta.url === `file://${process.argv[1]}`) {
  main().catch(console.error);
}
