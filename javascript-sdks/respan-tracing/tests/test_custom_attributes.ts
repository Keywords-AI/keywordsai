import * as dotenv from "dotenv";
const result = dotenv.config({ override: true });
import { RespanTelemetry } from "@respan/tracing";

const apiKey = process.env.RESPAN_API_KEY || "";
const baseURL = process.env.RESPAN_BASE_URL || "";
const appName = process.env.RESPAN_APP_NAME || "default";

const respan = new RespanTelemetry({
  apiKey,
  baseURL,
  appName,
  disableBatch: true,
});

async function testTask() {
  return await respan.withTask({ name: "test" }, async () => {
    console.log("test task");
    return "test task";
  });
}

async function testWorkflow() {
  return await respan.withWorkflow({ name: "test" }, async () => {
    respan.withRespanSpanAttributes(
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
