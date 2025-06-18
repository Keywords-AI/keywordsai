import * as dotenv from 'dotenv';

dotenv.config({
  path: '../../../.env',
  override: true
});

async function testDirectAPI() {
  const apiKey = process.env.KEYWORDSAI_API_KEY;
  const endpoint = 'https://api.keywordsai.co/api/openai/v1/traces/ingest';
  
  if (!apiKey) {
    console.error('KEYWORDSAI_API_KEY not found');
    return;
  }

  // Create a test payload that looks more like real OpenAI agent data
  const testPayload = {
    data: [
      {
        trace_unique_id: "test_trace_123",
        span_unique_id: "test_span_123",
        span_name: "response",
        log_type: "response",
        span_type: "openai_agent",
        model: "gpt-4",
        prompt_tokens: 10,
        completion_tokens: 5,
        total_request_tokens: 15,
        input: "Hello world",
        output: "Hi there!",
        timestamp: new Date().toISOString(),
        start_time: new Date(Date.now() - 1000).toISOString(),
        latency: 1.0,
        status_code: 200,
        error_bit: 0,
        prompt_messages: [
          {
            role: "user",
            content: "Hello world"
          }
        ],
        completion_messages: [
          {
            role: "assistant", 
            content: "Hi there!"
          }
        ]
      }
    ]
  };

  console.log('Testing direct API call...');
  console.log('Endpoint:', endpoint);
  console.log('API Key:', apiKey.substring(0, 10) + '...');
  console.log('Payload:', JSON.stringify(testPayload, null, 2));

  try {
    const response = await fetch(endpoint, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${apiKey}`,
        'Content-Type': 'application/json',
        'OpenAI-Beta': 'traces=v1',
        'X-Source': 'openai-agents-sdk'
      },
      body: JSON.stringify(testPayload)
    });

    console.log('Response status:', response.status);
    console.log('Response headers:', response.headers);
    
    const responseText = await response.text();
    console.log('Response body:', responseText);
    
    if (response.ok) {
      console.log('✅ API call successful!');
    } else {
      console.log('❌ API call failed');
    }
  } catch (error) {
    console.error('Error:', error);
  }
}

testDirectAPI(); 