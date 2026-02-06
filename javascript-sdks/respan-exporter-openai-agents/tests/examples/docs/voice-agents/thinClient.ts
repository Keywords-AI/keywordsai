import { OpenAIRealtimeWebRTC } from '@openai/agents/realtime';

const client = new OpenAIRealtimeWebRTC();
const audioBuffer = new ArrayBuffer(0);

await client.connect({
  apiKey: '<api key>',
  model: 'gpt-4o-mini-realtime-preview',
  initialSessionConfig: {
    instructions: 'Speak like a pirate',
    voice: 'ash',
    modalities: ['text', 'audio'],
    inputAudioFormat: 'pcm16',
    outputAudioFormat: 'pcm16',
  },
});

// optionally for WebSockets
client.on('audio', (newAudio) => {});

client.sendAudio(audioBuffer);
