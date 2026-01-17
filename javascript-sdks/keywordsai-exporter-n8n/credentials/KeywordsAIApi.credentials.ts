import type {
	IAuthenticateGeneric,
	Icon,
	ICredentialTestRequest,
	ICredentialType,
	INodeProperties,
} from 'n8n-workflow';

export class KeywordsAIApi implements ICredentialType {
	name = 'keywordsAIApi';

	displayName = 'Keywords AI API';

	icon: Icon = { light: 'file:../icons/keywordsai.svg', dark: 'file:../icons/keywordsai.dark.svg' };

	documentationUrl = 'https://docs.keywordsai.co/get-started/api-keys';

	properties: INodeProperties[] = [
		{
			displayName: 'API Key',
			name: 'apiKey',
			type: 'string',
			typeOptions: { password: true },
			default: '',
			required: true,
		},
	];

	authenticate: IAuthenticateGeneric = {
		type: 'generic',
		properties: {
			headers: {
				Authorization: '=Bearer {{$credentials?.apiKey}}',
			},
		},
	};

	test: ICredentialTestRequest = {
		request: {
			baseURL: 'https://api.keywordsai.co/api',
			url: '/models',
			method: 'GET',
		},
	};
}

