import { withWorkflow, withTask, withAgent, withTool } from "../src/decorators/index.js";
import { startTracing } from "../src/utils/tracing.js";

// Initialize tracing with debug logging to see the filtering in action
await startTracing({
  appName: "noise-filtering-demo",
  apiKey: process.env.RESPAN_API_KEY || "demo-key",
  baseURL: process.env.RESPAN_BASE_URL || "https://api.respan.ai",
  logLevel: "debug", // Enable debug logs to see filtering
});

console.log("🎯 Respan Noise Filtering Demo");
console.log("==================================");
console.log("This demo shows how the SDK filters out auto-instrumentation noise");
console.log("and only sends spans from your explicit decorators.\n");

// Example workflow that makes HTTP calls and other operations
// Without filtering, these would generate lots of HTTP spans, framework spans, etc.
const webSearchWorkflow = async (query: string) => {
  console.log(`🔍 Starting web search for: "${query}"`);
  
  // This tool will make HTTP calls - without filtering, you'd see HTTP spans
  const searchResults = await withTool(
    { name: "webSearch" },
    async (searchQuery: string) => {
      console.log(`  📡 Making HTTP request for: ${searchQuery}`);
      
      try {
        // This HTTP call would normally create auto-instrumentation spans
        const response = await fetch(`https://httpbin.org/json`);
        const data = await response.json();
        
        // Simulate processing
        await new Promise(resolve => setTimeout(resolve, 100));
        
        return {
          query: searchQuery,
          results: [`Result 1 for ${searchQuery}`, `Result 2 for ${searchQuery}`],
          metadata: data
        };
      } catch (error) {
        console.log(`  ❌ HTTP request failed: ${error}`);
        return { query: searchQuery, results: [], error: String(error) };
      }
    },
    query
  );
  
  // Process results with another task
  const processedResults = await withTask(
    { name: "processResults" },
    async (results: any) => {
      console.log(`  🔄 Processing ${results.results?.length || 0} results`);
      
      // Simulate some processing time
      await new Promise(resolve => setTimeout(resolve, 50));
      
      return {
        originalQuery: query,
        processed: true,
        summary: `Found ${results.results?.length || 0} results for "${query}"`,
        timestamp: new Date().toISOString()
      };
    },
    searchResults
  );
  
  return processedResults;
};

// Agent that orchestrates the workflow
const searchAgent = async (userQuery: string) => {
  return withAgent(
    { name: "searchAgent" },
    async (query: string) => {
      console.log(`🤖 Agent processing query: "${query}"`);
      
      // The agent calls the workflow
      const result = await webSearchWorkflow(query);
      
      console.log(`✅ Agent completed processing`);
      return {
        agent: "searchAgent",
        result,
        confidence: 0.95
      };
    },
    userQuery
  );
};

// Main workflow
const mainWorkflow = async () => {
  return withWorkflow(
    { name: "mainWorkflow" },
    async () => {
      console.log(`🚀 Starting main workflow`);
      
      const queries = ["artificial intelligence", "web development"];
      const results = [];
      
      for (const query of queries) {
        console.log(`\n--- Processing Query: ${query} ---`);
        const result = await searchAgent(query);
        results.push(result);
      }
      
      console.log(`\n🎉 Workflow completed with ${results.length} results`);
      return {
        workflow: "mainWorkflow",
        totalQueries: queries.length,
        results,
        completedAt: new Date().toISOString()
      };
    }
  );
};

// Run the demo
console.log("Running workflow with HTTP calls and nested operations...");
console.log("Watch the debug logs - you should only see spans for decorated functions:\n");

try {
  const result = await mainWorkflow();
  
  console.log("\n" + "=".repeat(50));
  console.log("🎯 FILTERING RESULTS");
  console.log("=".repeat(50));
  console.log("✅ Only the following spans should be sent to Respan:");
  console.log("   • mainWorkflow.workflow (root span)");
  console.log("   • searchAgent.agent (root span)");  
  console.log("   • webSearch.tool (root span)");
  console.log("   • processResults.task (root span)");
  console.log("\n✅ Child spans within withEntity context are preserved:");
  console.log("   • HTTP request spans from fetch() within workflows");
  console.log("   • Database calls within tasks");
  console.log("   • Any spans that occur within decorated functions");
  console.log("\n❌ The following spans are filtered out (not sent):");
  console.log("   • HTTP spans outside of withEntity context");
  console.log("   • Pure auto-instrumentation spans");
  console.log("   • Framework spans with no user context");
  
  console.log(`\n📊 Final Result Summary:`);
  console.log(`   Processed ${result.totalQueries} queries`);
  console.log(`   Completed at: ${result.completedAt}`);
  
} catch (error) {
  console.error("❌ Demo failed:", error);
}

console.log("\n💡 Key Benefits of Improved Noise Filtering:");
console.log("   1. User-decorated spans become clean root spans");  
console.log("   2. Child spans within your context are preserved");
console.log("   3. Pure auto-instrumentation noise is eliminated");
console.log("   4. Maintains useful tracing hierarchy within your workflows"); 