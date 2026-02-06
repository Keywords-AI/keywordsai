import { RealtimeSession, RealtimeAgent } from '@openai/agents/realtime';

const agent = new RealtimeAgent({
  name: 'Assistant',
});

const session = new RealtimeSession(agent, {
  model: 'gpt-4o-realtime-preview-2025-06-03',
});

session.sendMessage('Hello, how are you?');
