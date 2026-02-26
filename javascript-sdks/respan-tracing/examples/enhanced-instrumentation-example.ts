import { RespanTelemetry } from "../src/main.js";

async function demonstrateEnhancedInstrumentation() {
  console.log("=== Enhanced Instrumentation Management Demo ===\n");

  // Example 1: Automatic Discovery (no warnings for missing packages)
  console.log("🔍 Example 1: Automatic Discovery (Silent Mode)");
  console.log("When no instrumentModules are specified, Respan automatically tries");
  console.log("to load all supported instrumentations without showing warnings for missing packages.\n");
  
  const autoDiscoveryClient = new RespanTelemetry({
    apiKey: process.env.RESPAN_API_KEY || "your-api-key",
    appName: "auto-discovery-demo",
    disabledInstrumentations: ['bedrock', 'chromaDB'], // Disable some we don't want
    logLevel: 'info'
  });

  await autoDiscoveryClient.initialize();
  console.log("✅ Auto-discovery completed - notice no installation warnings!\n");

  // Example 2: Explicit Module Specification (with warnings)
  console.log("⚠️  Example 2: Explicit Modules (Show Warnings)");
  console.log("When you explicitly specify modules, Respan will show warnings");
  console.log("for any that fail to load since you explicitly requested them.\n");

  const explicitClient = new RespanTelemetry({
    apiKey: process.env.RESPAN_API_KEY || "your-api-key",
    appName: "explicit-modules-demo",
    instrumentModules: {
      // These would normally be real imported modules:
      // openAI: OpenAI,
      // anthropic: Anthropic,
      // someCustomModule: MyCustomInstrumentation,
    },
    logLevel: 'info'
  });

  // Don't actually initialize to avoid conflicts in this demo
  console.log("(Would show installation warnings for missing explicitly specified modules)\n");

  // Example 3: Generic Custom Module Handling
  console.log("🎯 Example 3: Custom Module Support");
  console.log("Respan now tries to handle ANY module you provide, even if it's");
  console.log("not in our pre-defined list. It will:");
  console.log("1. Try calling manuallyInstrument() if the method exists");
  console.log("2. Otherwise treat it as an instrumentation instance");
  console.log("3. Show helpful errors if neither approach works\n");

  // Mock custom instrumentation for demonstration
  class MockCustomInstrumentation {
    manuallyInstrument(module: any) {
      console.log("🔧 Custom instrumentation applied!");
    }
  }

  const customModuleClient = new RespanTelemetry({
    apiKey: process.env.RESPAN_API_KEY || "your-api-key",
    appName: "custom-module-demo", 
    instrumentModules: {
      openAI: null, // Pre-defined module (would be OpenAI if imported)
      myCustomTool: new MockCustomInstrumentation(), // Custom module
      anotherCustom: { someProperty: 'value' }, // Another custom module
    },
    logLevel: 'info'
  });

  // Don't initialize to avoid complexity in demo
  console.log("(Would attempt generic instrumentation for custom modules)\n");

  console.log("🎉 Key Benefits of Enhanced System:");
  console.log("• Silent auto-discovery: No spam warnings for optional packages");
  console.log("• Smart warnings: Only warn when explicitly requested modules fail");
  console.log("• Generic support: Handle any OpenTelemetry instrumentation");
  console.log("• Better DX: Developers can mix pre-defined and custom modules");
  console.log("• Consistent API: Same manuallyInstrument() pattern everywhere");
}

demonstrateEnhancedInstrumentation().catch(console.error); 