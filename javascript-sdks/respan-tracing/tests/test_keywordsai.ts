import * as dotenv from "dotenv";
const result = dotenv.config({ override: true });
console.log(result);
import { KeywordsAITelemetry } from "../src/main";

const apiKey = process.env.KEYWORDSAI_API_KEY || "";
const baseURL = process.env.KEYWORDSAI_BASE_URL || "";
const appName = process.env.KEYWORDSAI_APP_NAME || "default";

const keywordsAi = new KeywordsAITelemetry({
  apiKey,
  baseURL,
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
    await testTask();
    return "test workflow";
  });
}

testWorkflow();
