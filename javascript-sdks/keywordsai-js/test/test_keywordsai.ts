import { KeywordsAITelemetry } from "../src/main";

const keywordsAi = new KeywordsAITelemetry({
    apiKey: process.env.KEYWORDS_AI_API_KEY || "",
    appName: process.env.KEYWORDS_AI_APP_NAME || "default",
});




async function testTask() {
    return await keywordsAi.withTask({name: "test"},async (task) => {
        console.log("test task");
        return testTask();
    });
}


async function testWorkflow() {
    return await keywordsAi.withWorkflow({name: "test"},async (workflow) => {
        testTask();
        return "test workflow";
    });
}

testWorkflow();