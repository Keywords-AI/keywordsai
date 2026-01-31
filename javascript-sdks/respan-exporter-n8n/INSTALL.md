# Clean Installation Guide

Follow these steps for a fresh installation of the Keywords AI node for n8n.

## Prerequisites Check

Before starting, ensure you have:

- [ ] Node.js v18+ installed: `node --version`
- [ ] npm installed: `npm --version`
- [ ] Keywords AI API Key from https://platform.keywordsai.co
- [ ] Git installed (if cloning): `git --version`

## Step 1: Get the Code

```bash
# Clone the repository
git clone <your-repo-url>
cd n8n-keywordsai

# OR if you downloaded a zip
unzip n8n-keywordsai.zip
cd n8n-keywordsai
```

## Step 2: Install Dependencies

```bash
npm install
```

**Expected output:** 
```
added X packages, and audited Y packages in Zs
found 0 vulnerabilities
```

## Step 3: Build the Node

```bash
npm run build
```

**Expected output:**
```
✓ Build successful
```

## Step 4: Setup n8n Custom Directory

```bash
# Create the custom directory
mkdir -p ~/.n8n/custom

# Navigate to it
cd ~/.n8n/custom

# Initialize npm if package.json doesn't exist
npm init -y
```

## Step 5: Link the Node

```bash
# From the n8n-keywordsai directory
cd /path/to/n8n-keywordsai
npm link

# Then link to n8n custom
cd ~/.n8n/custom
npm link n8n-nodes-keywordsai
```

**Verify the link:**
```bash
npm list n8n-nodes-keywordsai
```

You should see: `n8n-nodes-keywordsai@0.1.0 -> ./../../../../../path/to/n8n-keywordsai`

## Step 6: Start n8n

```bash
# From any directory
npx n8n start
```

**Wait for:**
```
Editor is now accessible via:
http://localhost:5678/
```

## Step 7: Configure Credentials in n8n

1. Open http://localhost:5678 in your browser
2. Click **Settings** (gear icon) → **Credentials**
3. Click **+ Add Credential**
4. Search for "Keywords AI" and select it
5. Enter your API Key
6. Click **Test** - should show "Connection tested successfully"
7. Click **Save**

## Step 8: Test the Node

1. Create a new workflow
2. Add a **Manual Trigger** node
3. Add a **Keywords AI** node
4. Connect them
5. Configure Keywords AI node:
   - Select your credentials
   - Choose **"Gateway with Prompt"**
   - Select a prompt (should load from your Keywords AI account)
   - Select a version
   - Fill in variable values
6. Click **Execute Node**

You should see a successful response!

## Verification Checklist

- [ ] `npm run build` completes successfully
- [ ] No errors when linking with `npm link`
- [ ] n8n starts without errors
- [ ] Keywords AI node appears in n8n's node list
- [ ] Credentials test successfully
- [ ] Node executes and returns data

## Troubleshooting

### Build Fails

```bash
rm -rf dist node_modules package-lock.json
npm install
npm run build
```

### Link Issues

```bash
# Unlink and relink
npm unlink n8n-nodes-keywordsai
cd /path/to/n8n-keywordsai
npm link
cd ~/.n8n/custom
npm link n8n-nodes-keywordsai
```

### n8n Won't Start

```bash
# Clear npm cache
npm cache clean --force
rm -rf ~/.npm/_npx

# Try again
npx n8n start
```

### Node Not Appearing in n8n

```bash
# Clear n8n cache
rm -rf ~/.n8n/cache

# Restart n8n
# Stop n8n (Ctrl+C)
npx n8n start
```

### Variables Not Loading

Make sure you:
1. Select a **Prompt** first
2. Then select a **Version**
3. Variables appear automatically

## Clean Uninstall

To completely remove and start over:

```bash
# 1. Stop n8n (Ctrl+C in terminal)

# 2. Unlink from n8n
cd ~/.n8n/custom
npm unlink n8n-nodes-keywordsai

# 3. Remove from global npm
npm unlink -g n8n-nodes-keywordsai

# 4. Clean the project
cd /path/to/n8n-keywordsai
rm -rf dist node_modules package-lock.json

# 5. Clean npm cache
npm cache clean --force

# 6. Now you can start fresh from Step 2
```

## Environment-Specific Notes

### macOS
- May need to prefix commands with `sudo` for global operations
- Use `~/.n8n/custom` for custom nodes

### Linux
- Same as macOS
- Ensure proper permissions on `~/.n8n` directory

### Windows
- Use `%USERPROFILE%\.n8n\custom` instead of `~/.n8n/custom`
- Use PowerShell or Git Bash
- Replace `/` with `\` in paths if using CMD

## Next Steps

After successful installation:

1. Create prompts in Keywords AI platform
2. Build workflows in n8n
3. Test with different models and prompts
4. Explore advanced features (streaming, overrides, etc.)

## Getting Help

- **Documentation**: https://docs.keywordsai.co
- **Issues**: Create an issue on GitHub
- **Support**: support@keywordsai.co

---

✅ Installation complete! Happy automating with Keywords AI + n8n!

