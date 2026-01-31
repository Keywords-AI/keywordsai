import type {
	IAuthenticateGeneric,
	Icon,
	ICredentialTestRequest,
	ICredentialType,
	INodeProperties,
} from 'n8n-workflow';

export class RespanApi implements ICredentialType {
	name = 'respanApi';

	displayName = 'Respan API';

	icon: Icon = { light: 'file:../icons/respan.svg', dark: 'file:../icons/respan.dark.svg' };

	documentationUrl = 'https://docs.respan.co/get-started/api-keys';

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
			baseURL: 'https://api.respan.co/api',
			url: '/models',
			method: 'GET',
		},
	};
}

