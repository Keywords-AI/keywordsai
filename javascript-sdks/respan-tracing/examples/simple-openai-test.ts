import OpenAI from "openai";
import * as dotenv from "dotenv";
import { KeywordsAITelemetry } from "../src/main.js";

dotenv.config({
    path: ".env",
    override: true
});
// Declare global type
declare global {
  var keywordsai: KeywordsAITelemetry | undefined;
}

const openai = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY || "test-api-key",
});

export interface ChatMessage {
  role: "user" | "assistant" | "system";
  content: string;
}

export async function generateChatCompletion(messages: ChatMessage[]) {
  // Access keywordsai from global object after instrumentation is initialized
  const keywordsai = global.keywordsai;
  
  if (!keywordsai) {
    throw new Error("KeywordsAI not initialized. Make sure instrumentation is set up correctly.");
  }

  return await keywordsai.withWorkflow(
    {
      name: "generateChatCompletion",
    },
    async (params) => {
      try {
        const completion = await openai.chat.completions.create({
          model: params.model,
          messages: messages,
          temperature: params.temperature,
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
    },
    {
        model: "gpt-3.5-turbo",
        messages: messages,
        temperature: 0.7
    }
  );
}

async function simpleOpenAITest() {
  console.log("🚀 Simple OpenAI + KeywordsAI Test\n");

  // Initialize KeywordsAI with OpenAI instrumentation
  const keywordsai = new KeywordsAITelemetry({
    apiKey: process.env.KEYWORDSAI_API_KEY || "test-api-key",
    appName: "simple-openai-test",
    instrumentModules: {
      openAI: OpenAI, // This enables OpenAI tracing
    },
    logLevel: 'info'
  });

  await keywordsai.initialize();
  
  // Set global instance
  global.keywordsai = keywordsai;
  console.log("✅ KeywordsAI setup complete\n");

  // Test your function
  const messages: ChatMessage[] = [
    { role: "system", content: "You are a helpful assistant." },
    { role: "user", content: "What is TypeScript?" },
  ];

  try {
    console.log("📤 Sending request to OpenAI...");
    const result = await generateChatCompletion(messages);
    
    console.log("✅ Success!");
    console.log("🤖 Response:", result.message);
    console.log("📊 Usage:", result.usage);
    console.log("🆔 ID:", result.id);
    
  } catch (error) {
    console.error("❌ Error:", error);
  }

  // Cleanup
  await keywordsai.shutdown();
  console.log("\n✅ Test completed!");
}

// Run the test
simpleOpenAITest().catch(console.error); 