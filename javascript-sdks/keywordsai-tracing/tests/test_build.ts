/**
 * Test the built package (from dist/)
 * 
 * To run this test:
 * 1. Build the package: npm run build
 * 2. Create tarball: npm pack
 * 3. Install locally: npm install ./keywordsai-tracing-*.tgz --no-save
 * 4. Run this test: tsx tests/test_build.ts
 */

import { KeywordsAITelemetry, getClient } from '@keywordsai/tracing';
import * as dotenv from 'dotenv';

dotenv.config();

console.log('=== Testing Built Package ===\n');

async function testBuiltPackage() {
  // Test 1: Basic import
  console.log('✓ Package imports successfully');
  
  // Test 2: Initialize
  const kai = new KeywordsAITelemetry({
    apiKey: process.env.KEYWORDSAI_API_KEY,
    baseURL: process.env.KEYWORDSAI_BASE_URL,
    appName: 'build-test',
    disableBatch: true,
    logLevel: 'info'
  });
  
  console.log('✓ KeywordsAITelemetry instantiated');
  
  await kai.initialize();
  console.log('✓ SDK initialized');
  
  // Test 3: Client API
  const client = getClient();
  console.log('✓ getClient() works');
  
  // Test 4: Decorators work
  await kai.withTask({ name: 'build_test_task' }, async () => {
    const traceId = client.getCurrentTraceId();
    const spanId = client.getCurrentSpanId();
    
    console.log(`✓ Trace ID: ${traceId}`);
    console.log(`✓ Span ID: ${spanId}`);
    
    client.updateCurrentSpan({
      keywordsaiParams: {
        customerIdentifier: 'test-user',
        metadata: { test: 'build' }
      }
    });
    console.log('✓ updateCurrentSpan() works');
    
    client.addEvent('test_event', { status: 'success' });
    console.log('✓ addEvent() works');
  });
  
  // Test 5: Span buffer
  const manager = kai.getSpanBufferManager();
  const buffer = manager.createBuffer('test-123');
  buffer.createSpan('test_span', { test: true });
  console.log(`✓ Span buffer works (${buffer.getSpanCount()} spans)`);
  
  await kai.shutdown();
  console.log('✓ SDK shutdown');
  
  console.log('\n=== All Build Tests Passed! ===');
}

testBuiltPackage().catch(console.error);
