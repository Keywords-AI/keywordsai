import * as traceloop from "@traceloop/node-server-sdk";
import { withAgent } from "@traceloop/node-server-sdk";
import OpenAI from "openai";
// Make sure to import the entire module you want to instrument, like this:
// import * as LlamaIndex from "llamaindex";
traceloop.initialize({
    appName: "app",
    disableBatch: true,
    baseUrl: "http://localhost:8000/api",
    apiKey: "q3L47zcc.YOjSCQTZxjJ0kOxpE7YOSSSyr70YiFsb",
    //   baseUrl: "https://webhook.site/f1193061-a409-4491-a253-ed01944249e4",
    //   apiKey: "7fdef9b08e595d3af475111c41054eecba42c48ec048bf2878150d8831a4b6b37300cc5b3677ba55b0c2bb2f88263c0e", // This is the traceloop key
    instrumentModules: {
        openAI: OpenAI,
        // Add any other modules you'd like to instrument here
        // for example:
        // llamaIndex: LlamaIndex,
    },
});
const openai = new OpenAI();
async function create_joke() {
    return await traceloop.withTask({ name: "joke_creation" }, async () => {
        const completion = await openai.chat.completions.create({
            model: "gpt-3.5-turbo",
            messages: [
                { role: "user", content: "Tell me a joke about opentelemetry" },
            ],
        });
        return completion.choices[0].message.content;
    });
}
async function generate_signature(joke) {
    return await traceloop.withTask({ name: "signature_generation" }, async () => {
        const completion = await openai.chat.completions.create({
            model: "gpt-3.5-turbo",
            messages: [
                {
                    role: "user",
                    content: `add a signature to the joke:\n\n${joke}`,
                },
            ],
        });
        return completion.choices[0].message.content;
    });
}
async function translate_joke_to_pirate(joke) {
    return await withAgent({ name: "joke_translation" }, async () => {
        const completion = await openai.chat.completions.create({
            model: "gpt-3.5-turbo",
            messages: [
                {
                    role: "user",
                    content: `Translate the below joke to pirate-like english:\n\n${joke}`,
                },
            ],
        });
        return completion.choices[0].message.content;
    });
}
async function joke_workflow() {
    return await traceloop.withWorkflow({ name: "pirate_joke_generator" }, async () => {
        //   const eng_joke = await create_joke();
        //   const pirate_joke = await translate_joke_to_pirate(eng_joke);
        //   const signature = await generate_signature(pirate_joke);
        //   console.log(pirate_joke + "\n\n" + signature);
        return "javascript";
    });
}
async function main() {
    await joke_workflow();
}
main();
//# sourceMappingURL=test_traceloop.js.map