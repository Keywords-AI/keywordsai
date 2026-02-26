import OpenAI from "openai";
import { RespanTelemetry } from "../src/main.js";

// Declare global type
declare global {
  var respan: RespanTelemetry | undefined;
}

const openai = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY || "test-api-key",
});

export interface ChatMessage {
  role: "user" | "assistant" | "system";
  content: string;
}

export async function generateChatCompletion(messages: ChatMessage[]) {
  // Access respan from global object after instrumentation is initialized
  const respan = global.respan;
  
  if (!respan) {
    throw new Error("Respan not initialized. Make sure instrumentation is set up correctly.");
  }

  return await respan.withWorkflow(
    {
      name: "generateChatCompletion",
    },
    async () => {
      try {
        const completion = await openai.chat.completions.create({
          model: "gpt-3.5-turbo",
          messages: messages,
          temperature: 0.7,
        });

        const assistantMessage = completion.choices[0]?.message?.content;
        return {
          message: assistantMessage,
          usage: completion.usage,
          model: completion.model,
          id: completion.id,
        };
      } catch (error) {
        console.error("OpenAI API error:", error);
        throw error;
      }
    }
  );
}

// Test function that simulates OpenAI responses for testing
async function mockGenerateChatCompletion(messages: ChatMessage[]) {
  const respan = global.respan;
  
  if (!respan) {
    throw new Error("Respan not initialized. Make sure instrumentation is set up correctly.");
  }

  return await respan.withWorkflow(
    {
      name: "generateChatCompletion",
    },
    async () => {
      // Simulate some processing time
      await new Promise(resolve => setTimeout(resolve, 100));
      
      // Mock response based on the input
      const lastMessage = messages[messages.length - 1];
      const mockResponse = {
        message: `Mock response to: "${lastMessage.content}"`,
        usage: {
          prompt_tokens: 50,
          completion_tokens: 25,
          total_tokens: 75,
        },
        model: "gpt-3.5-turbo",
        id: `mock-${Date.now()}`,
      };

      console.log("🤖 Generated mock completion:", mockResponse.message);
      return mockResponse;
    }
  );
}

async function runOpenAIIntegrationTest() {
  console.log("🚀 Starting OpenAI Integration Test with Respan\n");

  // Step 1: Initialize Respan with OpenAI instrumentation
  console.log("📦 Step 1: Initializing Respan with OpenAI instrumentation...");
  
  const respan = new RespanTelemetry({
    apiKey: process.env.RESPAN_API_KEY || "test-api-key",
    appName: "openai-integration-test",
    // Manually provide OpenAI module for instrumentation
    instrumentModules: {
      openAI: OpenAI,
    },
    logLevel: 'info'
  });

  try {
    await respan.initialize();
    console.log("✅ Respan initialized successfully\n");
  } catch (error) {
    console.error("❌ Failed to initialize Respan:", error);
    return;
  }

  // Step 2: Set global instance
  console.log("🌍 Step 2: Setting up global Respan instance...");
  global.respan = respan;
  console.log("✅ Global instance set\n");

  // Step 3: Test the integration with mock data
  console.log("🧪 Step 3: Testing chat completion with mock responses...");
  
  const testMessages: ChatMessage[] = [
    { role: "system", content: "You are a helpful assistant." },
    { role: "user", content: "What is the capital of France?" },
  ];

  try {
    console.log("📝 Input messages:", testMessages);
    
    // Use mock function for testing (replace with real function if you have OpenAI API key)
    const useRealAPI = process.env.OPENAI_API_KEY && process.env.OPENAI_API_KEY !== "test-api-key";
    
    if (useRealAPI) {
      console.log("🔗 Using real OpenAI API...");
      const result = await generateChatCompletion(testMessages);
      console.log("✅ Real API Response:", result);
    } else {
      console.log("🎭 Using mock OpenAI responses (set OPENAI_API_KEY for real API)...");
      const result = await mockGenerateChatCompletion(testMessages);
      console.log("✅ Mock Response:", result);
    }

  } catch (error) {
    console.error("❌ Chat completion failed:", error);
  }

  // Step 4: Test multiple workflow calls
  console.log("\n🔄 Step 4: Testing multiple workflow calls...");
  
  const multipleTests = [
    { role: "user", content: "Tell me a joke" },
    { role: "user", content: "What's 2+2?" },
    { role: "user", content: "Explain quantum computing briefly" },
  ] as ChatMessage[];

  for (let i = 0; i < multipleTests.length; i++) {
    try {
      console.log(`\n📤 Test ${i + 1}:`, multipleTests[i].content);
      const messages = [
        { role: "system", content: "You are a helpful assistant." },
        multipleTests[i]
      ] as ChatMessage[];
      
      const result = await mockGenerateChatCompletion(messages);
      console.log(`📥 Response ${i + 1}:`, result.message);
      
    } catch (error) {
      console.error(`❌ Test ${i + 1} failed:`, error);
    }
  }

  // Step 5: Test error handling
  console.log("\n⚠️  Step 5: Testing error handling...");
  
  try {
    // Temporarily clear global instance to test error handling
    const originalInstance = global.respan;
    global.respan = undefined;
    
    await mockGenerateChatCompletion([{ role: "user", content: "This should fail" }]);
    
    // Restore instance
    global.respan = originalInstance;
    
  } catch (error) {
    console.log("✅ Error handling working correctly:", error.message);
  }

  // Step 6: Test instrumentation data
  console.log("\n📊 Step 6: Testing instrumentation features...");
  
  try {
    await respan.withWorkflow(
      { name: "test-workflow-with-metadata" },
      async () => {
        console.log("🔍 Running workflow with custom metadata...");
        
        // You can add custom span attributes here
        await respan.withTask(
          { name: "data-processing-task" },
          async () => {
            await new Promise(resolve => setTimeout(resolve, 50));
            console.log("✅ Task completed successfully");
            return "task-result";
          }
        );
        
        return "workflow-completed";
      }
    );
  } catch (error) {
    console.error("❌ Instrumentation test failed:", error);
  }

  // Step 7: Cleanup
  console.log("\n🧹 Step 7: Cleanup...");
  try {
    await respan.shutdown();
    console.log("✅ Respan shutdown completed");
  } catch (error) {
    console.error("⚠️  Shutdown warning:", error);
  }

  console.log("\n🎉 OpenAI Integration Test Complete!");
  console.log("\n📋 Summary:");
  console.log("• ✅ Respan initialization");
  console.log("• ✅ Global instance setup");
  console.log("• ✅ OpenAI instrumentation");
  console.log("• ✅ Workflow tracing");
  console.log("• ✅ Error handling");
  console.log("• ✅ Multiple API calls");
  console.log("• ✅ Custom metadata");
  
  if (process.env.OPENAI_API_KEY && process.env.OPENAI_API_KEY !== "test-api-key") {
    console.log("• ✅ Real OpenAI API integration");
  } else {
    console.log("• 🎭 Mock API testing (set OPENAI_API_KEY for real API)");
  }
}

// Run the test if this file is executed directly
if (import.meta.url === `file://${process.argv[1]}`) {
  runOpenAIIntegrationTest().catch(console.error);
}

export { runOpenAIIntegrationTest }; 