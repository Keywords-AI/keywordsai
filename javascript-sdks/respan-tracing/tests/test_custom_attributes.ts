import * as dotenv from "dotenv";
const result = dotenv.config({ override: true });
import { KeywordsAITelemetry } from "@keywordsai/tracing";

const apiKey = process.env.KEYWORDSAI_API_KEY || "";
const baseURL = process.env.KEYWORDSAI_BASE_URL || "";
const appName = process.env.KEYWORDSAI_APP_NAME || "default";

const keywordsAI = new KeywordsAITelemetry({
  apiKey,
  baseURL,
  appName,
  disableBatch: true,
});

async function testTask() {
  return await keywordsAI.withTask({ name: "test" }, async () => {
    console.log("test task");
    return "test task";
  });
}

async function testWorkflow() {
  return await keywordsAI.withWorkflow({ name: "test" }, async () => {
    keywordsAI.withKeywordsAISpanAttributes(
      async () => {
        testTask();
      },
      {
        trace_group_identifier: "some_trace_group_identifier",
      }
    );
    return "test workflow";
  });
}

testWorkflow();
