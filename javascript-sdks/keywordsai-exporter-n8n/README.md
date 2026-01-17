# Keywords AI Node for n8n

A custom n8n node for integrating Keywords AI's LLM Gateway and Prompt Management features into your n8n workflows.

## Features

- 🚀 **Gateway (Standard)**: Make direct LLM calls with custom messages
- 📝 **Gateway with Prompt**: Use managed prompts from Keywords AI
- 🔄 **Auto-populated Variables**: Automatically fetch variable names from your prompts
- 📊 **Dynamic Version Selection**: Choose from live, draft, or specific prompt versions
- 🔐 **Secure Authentication**: API key-based authentication
- 🎯 **AI-Ready**: Works as an AI tool in n8n workflows

## Installation

### Prerequisites

- Node.js v18 or higher
- npm or yarn
- Keywords AI API Key ([Get one here](https://platform.keywordsai.co))

### Fresh Installation

1. **Clone the repository:**
   ```bash
   git clone <your-repo-url>
   cd n8n-keywordsai
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Build the node:**
   ```bash
   npm run build
   ```

4. **Link to n8n:**
   ```bash
   # Link the package globally
   npm link
   
   # Create n8n custom directory if it doesn't exist
   mkdir -p ~/.n8n/custom
   cd ~/.n8n/custom
   
   # Initialize if package.json doesn't exist
   npm init -y
   
   # Link the Keywords AI node
   npm link n8n-nodes-keywordsai
   ```

5. **Start n8n:**
   ```bash
   npx n8n start
   ```

6. **Access n8n:**
   Open http://localhost:5678 in your browser

## Usage

### Setup Credentials

1. In n8n, go to **Settings** → **Credentials**
2. Click **+ Add Credential**
3. Search for **"Keywords AI"**
4. Enter your API Key
5. Click **Test** to verify
6. Click **Save**

### Gateway (Standard)

Direct LLM calls without using saved prompts:

1. Add **Keywords AI** node to your workflow
2. Select **"Gateway (Standard)"**
3. Configure:
   - **Model**: `gpt-4o-mini` (or any supported model)
   - **System Message**: Your system prompt
   - **Messages**: Add user/assistant messages
4. Execute the node

### Gateway with Prompt

Use your managed prompts from Keywords AI:

1. Add **Keywords AI** node to your workflow
2. Select **"Gateway with Prompt"**
3. Configure:
   - **Prompt Name or ID**: Select from dropdown (auto-populated)
   - **Version**: Choose version (auto-populated)
   - **Variables**: Fill in values (names auto-populated from prompt)
4. Execute the node

### Observability & Tracking

Track and monitor your LLM calls with built-in observability parameters:

- **Metadata**: Custom key-value pairs for reference
- **Custom Identifier**: Fast, indexed tags for log filtering
- **Customer Identifier**: Track per-user usage and costs
- **Customer Params**: Detailed user info with budget tracking
- **Request Breakdown**: Get metrics (tokens, cost, latency) in response

See [OBSERVABILITY_GUIDE.md](./OBSERVABILITY_GUIDE.md) for detailed documentation.

### Example Workflow

```
Manual Trigger → Keywords AI → Send Email
```

## Development

### Project Structure

```
n8n-keywordsai/
├── nodes/
│   └── KeywordsAi/
│       ├── KeywordsAi.node.ts       # Main node logic
│       └── KeywordsAi.node.json     # Node metadata
├── credentials/
│   └── KeywordsAIApi.credentials.ts # Credentials definition
├── icons/
│   ├── keywordsai.svg              # Light theme icon
│   └── keywordsai.dark.svg         # Dark theme icon
├── dist/                            # Compiled output (gitignored)
├── package.json
└── README.md
```

### Build Commands

```bash
# Build the node
npm run build

# Lint the code
npm run lint

# Auto-fix linting issues
npm run lint:fix

# Watch mode (development)
npm run watch
```

### Making Changes

1. Make your changes to the TypeScript files
2. Build: `npm run build`
3. Restart n8n to see changes

### Clean Reinstall

If you need to start fresh:

```bash
# In the project directory
cd /path/to/n8n-keywordsai

# Remove build artifacts and dependencies
rm -rf dist node_modules package-lock.json

# Clear npm cache
npm cache clean --force

# Reinstall
npm install

# Rebuild
npm run build

# Relink
npm link
cd ~/.n8n/custom
npm link n8n-nodes-keywordsai

# Restart n8n
npx n8n start
```

## API Reference

This node uses the following Keywords AI API endpoints:

- `GET /api/prompts/` - List all prompts
- `GET /api/prompts/<prompt_id>/versions/` - List prompt versions
- `GET /api/prompts/<prompt_id>/versions/<version>/` - Get specific version
- `POST /api/chat/completions` - Make LLM calls

## Troubleshooting

### Node not showing in n8n

1. Ensure the node is built: `npm run build`
2. Check the link: `cd ~/.n8n/custom && npm list n8n-nodes-keywordsai`
3. Clear n8n cache: `rm -rf ~/.n8n/cache`
4. Restart n8n

### Variables not loading

Make sure you select:
1. A **Prompt** first
2. Then a **Version**

Variables load after version selection.

### Build errors

```bash
# Clean everything and rebuild
rm -rf dist node_modules
npm install
npm run build
```

### npm cache issues

```bash
npm cache clean --force
rm -rf ~/.npm/_npx
```

## Documentation

- [Keywords AI Documentation](https://docs.keywordsai.co)
- [Keywords AI Platform](https://platform.keywordsai.co)
- [n8n Community Nodes Guide](https://docs.n8n.io/integrations/community-nodes/)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

[Your License Here]

## Support

For issues and questions:
- Keywords AI: [support@keywordsai.co](mailto:support@keywordsai.co)
- GitHub Issues: [Create an issue](https://github.com/your-repo/issues)

## Credits

Built with ❤️ for the n8n and Keywords AI communities.
