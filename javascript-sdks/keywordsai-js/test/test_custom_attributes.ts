import * as dotenv from "dotenv";
const result = dotenv.config({ override: true });
console.log(result);
import { KeywordsAITelemetry } from "../src/main";

const apiKey = process.env.KEYWORDSAI_API_KEY || "";
const baseUrl = process.env.KEYWORDSAI_BASE_URL || "";
const appName = process.env.KEYWORDS_AI_APP_NAME || "default";

const keywordsAi = new KeywordsAITelemetry({
  apiKey,
  baseUrl,
  appName,
  disableBatch: true,
});

async function testTask() {
  return await keywordsAi.withTask({ name: "test" }, async (task) => {
    console.log("test task");
    return "test task";
  });
}

async function testWorkflow() {
  return await keywordsAi.withWorkflow({ name: "test" }, async (workflow) => {
    keywordsAi.withKeywordsAISpanAttributes(
      async () => {
        testTask();
      },
      {
        customer_identifier: "123",
        customer_email: "test@test.com",
        customer_name: "Test User",
        custom_identifier: "some_identifier",
        evaluation_identifier: "some_evaluation_identifier",
        thread_identifier: "some_thread_identifier",
        metadata: {
          key: "value",
        },
      }
    );
    return "test workflow";
  });
}

testWorkflow();
