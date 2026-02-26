import { RespanTelemetry } from "../src/main.js";

async function demonstrateExplicitModules() {
  console.log("=== Explicit Module Demo (Shows Warnings) ===\n");

  console.log("This example demonstrates the difference in warning behavior:");
  console.log("When you explicitly provide instrumentModules, Respan will warn");
  console.log("about modules that fail to initialize since you specifically requested them.\n");

  // Mock a custom instrumentation class for demonstration
  class MockCustomInstrumentation {
    constructor(public name: string) {}
    
    manuallyInstrument(module: any) {
      console.log(`[${this.name}] Manual instrumentation applied to:`, typeof module);
    }
  }

  const explicitClient = new RespanTelemetry({
    apiKey: process.env.RESPAN_API_KEY || "your-api-key",
    appName: "explicit-modules-demo",
    // Explicitly provide some modules (mix of null and custom)
    instrumentModules: {
      openAI: null, // This will trigger a warning since we explicitly asked for it but didn't provide it
      anthropic: null, // This will also trigger a warning
      myCustomAnalyzer: new MockCustomInstrumentation("CustomAnalyzer"), // Custom module with manuallyInstrument
      myOtherTool: { instrumentationName: "MyOtherTool" }, // Custom module without manuallyInstrument
    },
    logLevel: 'info'
  });

  console.log("Initializing with explicit modules...\n");
  
  // This will show warnings for the null modules since they were explicitly specified
  await explicitClient.initialize();
  
  console.log("\n✅ Notice the difference:");
  console.log("• Explicit null modules show installation warnings");
  console.log("• Custom modules are handled generically");
  console.log("• Failed custom modules show helpful error messages");
}

demonstrateExplicitModules().catch(console.error); 