import { OpenAI } from 'openai';
import { setDefaultOpenAIClient } from '@openai/agents';

const customClient = new OpenAI({ baseURL: '...', apiKey: '...' });
setDefaultOpenAIClient(customClient);
