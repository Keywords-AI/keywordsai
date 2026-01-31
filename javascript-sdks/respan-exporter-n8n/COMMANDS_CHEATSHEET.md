# Commands Cheat Sheet

Quick reference for common operations with the Keywords AI node.

## 📦 Installation

```bash
# Clone repository
git clone <repo-url>
cd n8n-keywordsai

# Install dependencies
npm install

# Build the node
npm run build

# Link to n8n
npm link
cd ~/.n8n/custom && npm link n8n-nodes-keywordsai

# Start n8n
npx n8n start
```

## 🔨 Development

```bash
# Build
npm run build

# Lint
npm run lint

# Auto-fix linting
npm run lint:fix

# Watch mode (auto-rebuild on changes)
npm run build:watch
```

## 🧹 Clean Up

```bash
# Remove build artifacts
rm -rf dist

# Remove dependencies
rm -rf node_modules

# Full clean
rm -rf dist node_modules package-lock.json

# Clear npm cache
npm cache clean --force

# Clear n8n cache
rm -rf ~/.n8n/cache
```

## 🔄 Reinstall

```bash
# Full reinstall
rm -rf dist node_modules package-lock.json
npm install
npm run build
npm link
cd ~/.n8n/custom && npm link n8n-nodes-keywordsai
```

## 🔗 Linking

```bash
# Link from project directory
cd /path/to/n8n-keywordsai
npm link

# Link to n8n
cd ~/.n8n/custom
npm link n8n-nodes-keywordsai

# Verify link
npm list n8n-nodes-keywordsai

# Unlink
cd ~/.n8n/custom
npm unlink n8n-nodes-keywordsai
```

## 🚀 n8n Operations

```bash
# Start n8n
npx n8n start

# Start n8n with custom port
npx n8n start --port 5679

# Start n8n in tunnel mode (public URL)
npx n8n start --tunnel

# Stop n8n
# Press Ctrl+C in the terminal
```

## 🐛 Troubleshooting

```bash
# Node not appearing?
rm -rf ~/.n8n/cache
# Then restart n8n

# Build failing?
rm -rf dist node_modules
npm install
npm run build

# npm cache issues?
npm cache clean --force
rm -rf ~/.npm/_npx

# Link issues?
npm unlink n8n-nodes-keywordsai
cd /path/to/n8n-keywordsai && npm link
cd ~/.n8n/custom && npm link n8n-nodes-keywordsai
```

## 📊 Project Info

```bash
# Check Node.js version
node --version

# Check npm version
npm --version

# List installed packages
npm list --depth=0

# Check for outdated packages
npm outdated

# Audit for vulnerabilities
npm audit
```

## 🔍 Testing

```bash
# Test API connection (replace with your key)
curl -H "Authorization: Bearer YOUR_API_KEY" \
  https://api.keywordsai.co/api/prompts/

# Check if node is linked
cd ~/.n8n/custom
npm list n8n-nodes-keywordsai
```

## 📝 Git Operations

```bash
# Check status
git status

# Add all files
git add .

# Commit
git commit -m "Your message"

# Push
git push origin main

# Pull latest
git pull origin main

# Create new branch
git checkout -b feature-name
```

## 📁 Directory Reference

| Path | Purpose |
|------|---------|
| `/path/to/n8n-keywordsai` | Your node source code |
| `~/.n8n/custom` | n8n custom nodes directory |
| `~/.n8n/cache` | n8n cache (safe to delete) |
| `~/.npm` | npm global cache |

## 🔑 Environment Variables

```bash
# Set custom n8n directory
export N8N_USER_FOLDER=~/my-n8n

# Set custom port
export N8N_PORT=5679

# Enable debug mode
export N8N_LOG_LEVEL=debug
```

## 📱 Quick Workflows

### After Making Code Changes
```bash
npm run build
# Restart n8n (Ctrl+C then npx n8n start)
```

### Fresh Install on New Machine
```bash
git clone <repo>
cd n8n-keywordsai
npm install && npm run build && npm link
cd ~/.n8n/custom && npm link n8n-nodes-keywordsai
npx n8n start
```

### Complete Reset
```bash
# Stop n8n first (Ctrl+C)
cd ~/.n8n/custom && npm unlink n8n-nodes-keywordsai
cd /path/to/n8n-keywordsai
rm -rf dist node_modules
npm cache clean --force
npm install && npm run build && npm link
cd ~/.n8n/custom && npm link n8n-nodes-keywordsai
npx n8n start
```

## 🌐 URLs

| Service | URL |
|---------|-----|
| Local n8n | http://localhost:5678 |
| Keywords AI Platform | https://platform.keywordsai.co |
| Keywords AI Docs | https://docs.keywordsai.co |
| n8n Docs | https://docs.n8n.io |

## 💡 Tips

- Always `npm run build` after code changes
- Restart n8n to see node updates
- Clear `~/.n8n/cache` if node doesn't appear
- Use `npx n8n start --tunnel` for public access
- Check `npm list n8n-nodes-keywordsai` to verify link

---

**Pro Tip**: Save this file for quick reference during development!

