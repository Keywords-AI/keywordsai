import { KeywordsAITelemetry } from "../src/main.js";

async function example() {
  console.log("=== Example 1: Disable specific instrumentations ===");
  
  const keywordsAI = new KeywordsAITelemetry({
    apiKey: process.env.KEYWORDSAI_API_KEY || "your-api-key",
    appName: "instrumentation-management-example",
    // Disable certain instrumentations you don't want to use
    disabledInstrumentations: ['bedrock', 'chromaDB', 'qdrant'],
    // Set to debug level to see detailed loading information
    logLevel: 'info'
  });

  await keywordsAI.initialize();
  console.log("KeywordsAI initialized with disabled instrumentations");

  console.log("\n=== Example 2: Using manual instrumentation with disabled modules ===");
  
  // Example with manual instrumentation and some disabled modules
  // You would typically import your actual modules here
  // import OpenAI from 'openai';
  // import Anthropic from '@anthropic-ai/sdk';
  
  const keywordsAI2 = new KeywordsAITelemetry({
    apiKey: process.env.KEYWORDSAI_API_KEY || "your-api-key", 
    appName: "manual-instrumentation-example",
    // Manually provide modules (you would use real imported modules)
    instrumentModules: {
      // openAI: OpenAI,
      // anthropic: Anthropic,
    },
    // Even with manual instrumentation, you can disable specific ones
    disabledInstrumentations: ['langChain', 'llamaIndex'],
    logLevel: 'info'
  });

  console.log("This example shows how instrumentation loading works:");
  console.log("- Look for 'Successfully loaded:' messages to see what's available");
  console.log("- Look for 'install the required package' messages to see what's missing");
  console.log("- Look for 'Disabled instrumentations:' to see what you've blocked");
  
  // Note: Don't actually initialize the second one to avoid conflicts in this example
  // await keywordsAI2.initialize();
}

example().catch(console.error); 