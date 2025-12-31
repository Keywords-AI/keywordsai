import {
	IExecuteFunctions,
	ILoadOptionsFunctions,
	INodeExecutionData,
	INodePropertyOptions,
	INodeType,
	INodeTypeDescription,
	NodeConnectionTypes,
} from 'n8n-workflow';

export class KeywordsAi implements INodeType {
	description: INodeTypeDescription = {
		displayName: 'Keywords AI',
		name: 'keywordsAi',
		icon: { light: 'file:../../icons/keywordsai.svg', dark: 'file:../../icons/keywordsai.dark.svg' },
		group: ['transform'],
		version: 1,
		description: 'Keywords AI API integration',
		defaults: {
			name: 'Keywords AI',
		},
		inputs: [NodeConnectionTypes.Main],
		outputs: [NodeConnectionTypes.Main],
		credentials: [
			{
				name: 'keywordsAIApi',
				required: true,
			},
		],
		properties: [
			{
				displayName: 'Resource',
				name: 'resource',
				type: 'options',
				noDataExpression: true,
				options: [
					{
						name: 'Gateway (Standard)',
						value: 'gateway',
						description: 'Make a direct LLM call with messages',
					},
					{
						name: 'Gateway with Prompt',
						value: 'gatewayPrompt',
						description: 'Use a managed prompt from Keywords AI',
					},
				],
				default: 'gatewayPrompt',
			},

			// GATEWAY (Standard) PROPERTIES
			{
				displayName: 'Model',
				name: 'model',
				type: 'string',
				required: true,
				displayOptions: {
					show: {
						resource: ['gateway'],
					},
				},
				default: 'gpt-4o-mini',
				description: 'The model to use (e.g., gpt-4o, claude-3-5-sonnet)',
			},
			{
				displayName: 'System Message',
				name: 'systemMessage',
				type: 'string',
				typeOptions: {
					rows: 3,
				},
				displayOptions: {
					show: {
						resource: ['gateway'],
					},
				},
				default: 'You are a helpful assistant.',
				description: 'The system prompt to set the behavior of the AI',
			},
			{
				displayName: 'Messages',
				name: 'messages',
				type: 'fixedCollection',
				typeOptions: {
					multipleValues: true,
				},
				displayOptions: {
					show: {
						resource: ['gateway'],
					},
				},
				default: {},
				placeholder: 'Add Message',
				options: [
					{
						name: 'messageValues',
						displayName: 'Message',
						values: [
							{
								displayName: 'Role',
								name: 'role',
								type: 'options',
								options: [
									{ name: 'User', value: 'user' },
									{ name: 'Assistant', value: 'assistant' },
								],
								default: 'user',
							},
							{
								displayName: 'Content',
								name: 'content',
								type: 'string',
								required: true,
								default: '',
							},
						],
					},
				],
				description: 'The conversation history (User and Assistant messages)',
			},

			// GATEWAY WITH PROMPT PROPERTIES
			{
				displayName: 'Prompt Name or ID',
				name: 'promptId',
				type: 'options',
				required: true,
				typeOptions: {
					loadOptionsMethod: 'getPrompts',
				},
				displayOptions: {
					show: {
						resource: ['gatewayPrompt'],
					},
				},
				default: '',
				description: 'Choose from the list, or specify an ID using an <a href="https://docs.n8n.io/code/expressions/">expression</a>',
			},
			{
				displayName: 'Version Name or ID',
				name: 'version',
				type: 'options',
				typeOptions: {
					loadOptionsMethod: 'getVersions',
					loadOptionsDependsOn: ['promptId'],
				},
				displayOptions: {
					show: {
						resource: ['gatewayPrompt'],
					},
				},
				default: '',
				description: 'Choose from the list, or specify an ID using an <a href="https://docs.n8n.io/code/expressions/">expression</a>',
			},
			{
				displayName: 'Variables',
				name: 'variables',
				type: 'fixedCollection',
				typeOptions: {
					multipleValues: true,
				},
				displayOptions: {
					show: {
						resource: ['gatewayPrompt'],
					},
				},
				default: {},
				placeholder: 'Add Variable',
				options: [
					{
						name: 'variableValues',
						displayName: 'Variable',
						values: [
							{
								displayName: 'Variable Name or ID',
								name: 'name',
								type: 'options',
								typeOptions: {
									loadOptionsMethod: 'getVariables',
									loadOptionsDependsOn: ['promptId', 'version'],
								},
								default: '',
								description:
									'Choose from the list, or specify an ID using an <a href="https://docs.n8n.io/code/expressions/">expression</a>',
							},
							{
								displayName: 'Value',
								name: 'value',
								type: 'string',
								default: '',
								description: 'The value for this variable',
							},
						],
					},
				],
				description: 'Fill in values for variables defined in your prompt',
			},
			{
				displayName: 'Override Prompt Config',
				name: 'override',
				type: 'boolean',
				displayOptions: {
					show: {
						resource: ['gatewayPrompt'],
					},
				},
				default: false,
				description: 'Whether your prompt configuration overrides parameters like model and messages',
			},

			// SHARED ADDITIONAL FIELDS
			{
				displayName: 'Additional Fields',
				name: 'additionalFields',
				type: 'collection',
				placeholder: 'Add Field',
				default: {},
				options: [
					{
						displayName: 'Custom Identifier',
						name: 'customIdentifier',
						type: 'string',
						default: '',
						description: 'Custom tag to identify and filter logs faster (indexed field)',
					},
					{
						displayName: 'Customer Identifier',
						name: 'customerIdentifier',
						type: 'string',
						default: '',
						description: 'Tag to identify the user associated with this API call',
					},
					{
						displayName: 'Customer Params (JSON)',
						name: 'customerParams',
						type: 'string',
						default: '',
						description: 'JSON object with customer parameters like name, email, budget (e.g. {"customer_identifier": "user_123", "name": "John", "email": "john@example.com"})',
					},
					{
						displayName: 'Metadata (JSON)',
						name: 'metadata',
						type: 'string',
						default: '',
						description: 'JSON object with key-value pairs for reference (e.g. {"session_id": "123", "user_type": "premium"})',
					},
					{
						displayName: 'Override Params (JSON)',
						name: 'overrideParamsJson',
						type: 'string',
						default: '',
						description: 'JSON object with parameters (e.g. {"temperature": 0.5})',
					},
					{
						displayName: 'Request Breakdown',
						name: 'requestBreakdown',
						type: 'boolean',
						default: false,
						description: 'Whether to return detailed metrics in the response (tokens, cost, latency, etc.)',
					},
					{
						displayName: 'Stream',
						name: 'stream',
						type: 'boolean',
						default: false,
						description: 'Whether to stream back partial progress token by token',
					},
				],
			},
		],
		usableAsTool: true,
	};

	methods = {
		loadOptions: {
			async getPrompts(this: ILoadOptionsFunctions): Promise<INodePropertyOptions[]> {
				const responseData = await this.helpers.httpRequestWithAuthentication.call(this, 'keywordsAIApi', {
					method: 'GET',
					baseURL: 'https://api.keywordsai.co/api',
					url: '/prompts/',
					json: true,
				});
				
				let prompts: Array<{ name?: string; prompt_id: string }> = [];
				
				if (Array.isArray(responseData)) {
					prompts = responseData as Array<{ name?: string; prompt_id: string }>;
				} else if (responseData && typeof responseData === 'object') {
					const data = responseData as Record<string, unknown>;
					if (Array.isArray(data.results)) {
						prompts = data.results;
					} else if (Array.isArray(data.data)) {
						prompts = data.data;
					} else if (Array.isArray(data.prompts)) {
						prompts = data.prompts;
					}
				}
				
				return prompts.map((prompt) => ({
					name: prompt.name || prompt.prompt_id,
					value: prompt.prompt_id,
				}));
			},
			
			async getVersions(this: ILoadOptionsFunctions): Promise<INodePropertyOptions[]> {
				const promptId = this.getCurrentNodeParameter('promptId') as string;
				if (!promptId) return [];
				
				const responseData = await this.helpers.httpRequestWithAuthentication.call(this, 'keywordsAIApi', {
					method: 'GET',
					baseURL: 'https://api.keywordsai.co/api',
					url: `/prompts/${promptId}/versions/`,
					json: true,
				});
				
				let versions: Array<{ version: number; readonly?: boolean }> = [];
				
				if (Array.isArray(responseData)) {
					versions = responseData as Array<{ version: number; readonly?: boolean }>;
				} else if (responseData && typeof responseData === 'object') {
					const data = responseData as Record<string, unknown>;
					if (Array.isArray(data.results)) {
						versions = data.results;
					} else if (Array.isArray(data.data)) {
						versions = data.data;
					} else if (Array.isArray(data.versions)) {
						versions = data.versions;
					}
				}
				
				const options: INodePropertyOptions[] = versions.map((v) => ({
					name: `Version ${v.version}${v.readonly ? ' (Live)' : ''}`,
					value: v.version,
				}));
				options.unshift({ name: 'Latest (Draft)', value: 'latest' });
				return options;
			},
			
			async getVariables(this: ILoadOptionsFunctions): Promise<INodePropertyOptions[]> {
				const promptId = this.getCurrentNodeParameter('promptId') as string;
				const version = this.getCurrentNodeParameter('version') as string;
				
				if (!promptId || !version) return [];
				
				// For "latest", we need to get the current version from the versions list
				let versionNumber = version;
				if (version === 'latest') {
					const versionsData = await this.helpers.httpRequestWithAuthentication.call(this, 'keywordsAIApi', {
						method: 'GET',
						baseURL: 'https://api.keywordsai.co/api',
						url: `/prompts/${promptId}/versions/`,
						json: true,
					});
					
					let versions: Array<{ version: number }> = [];
					const data = versionsData as Record<string, unknown>;
					if (Array.isArray(data.results)) {
						versions = data.results;
					}
					
					if (versions.length > 0) {
						// Get the highest version number
						versionNumber = Math.max(...versions.map(v => v.version)).toString();
					}
				}
				
				const versionData = await this.helpers.httpRequestWithAuthentication.call(this, 'keywordsAIApi', {
					method: 'GET',
					baseURL: 'https://api.keywordsai.co/api',
					url: `/prompts/${promptId}/versions/${versionNumber}/`,
					json: true,
				});
				
				const data = versionData as { variables?: Record<string, string> };
				const variables = data.variables || {};
				
				return Object.keys(variables).map((varName) => ({
					name: varName,
					value: varName,
				}));
			},
		},
	};

	async execute(this: IExecuteFunctions): Promise<INodeExecutionData[][]> {
		const items = this.getInputData();
		const returnData: INodeExecutionData[] = [];

		for (let i = 0; i < items.length; i++) {
			try {
				const resource = this.getNodeParameter('resource', i) as string;
				const additionalFields = this.getNodeParameter('additionalFields', i) as {
					overrideParamsJson?: string;
					stream?: boolean;
					metadata?: string;
					customIdentifier?: string;
					customerIdentifier?: string;
					customerParams?: string;
					requestBreakdown?: boolean;
				};
				let body: {
					model?: string;
					messages?: Array<{ role: string; content: string }>;
					prompt?: {
						prompt_id: string;
						variables: { [key: string]: string };
						override: boolean;
						version?: string | number;
						override_params?: object;
					};
					stream?: boolean;
					metadata?: object;
					custom_identifier?: string;
					customer_identifier?: string;
					customer_params?: object;
					request_breakdown?: boolean;
				} = {};

				if (resource === 'gateway') {
					const model = this.getNodeParameter('model', i) as string;
					const systemMessage = this.getNodeParameter('systemMessage', i) as string;
					const messagesData = this.getNodeParameter('messages', i) as {
						messageValues?: Array<{ role: string; content: string }>;
					};

					const messages = [{ role: 'system', content: systemMessage }];
					if (messagesData?.messageValues) {
						for (const m of messagesData.messageValues) {
							messages.push({ role: m.role, content: m.content });
						}
					}
					body = { model, messages };
				} else {
					const promptId = this.getNodeParameter('promptId', i) as string;
					const variablesData = this.getNodeParameter('variables', i) as {
						variableValues?: Array<{ name: string; value: string }>;
					};
					const version = this.getNodeParameter('version', i) as string;
					const override = this.getNodeParameter('override', i) as boolean;

					const variables: { [key: string]: string } = {};
					if (variablesData?.variableValues) {
						for (const v of variablesData.variableValues) {
							variables[v.name] = v.value;
						}
					}
					body.prompt = { prompt_id: promptId, variables, override };
					if (version) body.prompt.version = version;
				}

				// Handle override params
				if (additionalFields.overrideParamsJson) {
					const params = JSON.parse(additionalFields.overrideParamsJson);
					if (resource === 'gatewayPrompt' && body.prompt) body.prompt.override_params = params;
					else Object.assign(body, params);
				}
				
				// Handle stream
				if (additionalFields.stream !== undefined) body.stream = additionalFields.stream;
				
				// Handle observability parameters
				if (additionalFields.metadata) {
					body.metadata = JSON.parse(additionalFields.metadata);
				}
				if (additionalFields.customIdentifier) {
					body.custom_identifier = additionalFields.customIdentifier;
				}
				if (additionalFields.customerIdentifier) {
					body.customer_identifier = additionalFields.customerIdentifier;
				}
				if (additionalFields.customerParams) {
					body.customer_params = JSON.parse(additionalFields.customerParams);
				}
				if (additionalFields.requestBreakdown !== undefined) {
					body.request_breakdown = additionalFields.requestBreakdown;
				}

				const responseData = await this.helpers.httpRequestWithAuthentication.call(this, 'keywordsAIApi', {
					method: 'POST',
					baseURL: 'https://api.keywordsai.co/api',
					url: '/chat/completions',
					body,
					json: true,
				});
				returnData.push({ json: responseData as INodeExecutionData['json'] });
			} catch (error) {
				if (this.continueOnFail()) {
					const err = error as Error;
					returnData.push({ json: { error: err.message } });
					continue;
				}
				throw error;
			}
		}
		return [returnData];
	}
}
