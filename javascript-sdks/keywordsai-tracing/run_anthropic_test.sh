#!/bin/bash

# Anthropic Instrumentation Test Runner
# This script helps set up and run the Anthropic instrumentation test

set -e  # Exit on error

echo "========================================="
echo "🧪 Anthropic Instrumentation Test Runner"
echo "========================================="
echo ""

# Check if we're in the right directory
if [ ! -f "package.json" ]; then
    echo "❌ Error: package.json not found"
    echo "   Please run this script from the keywordsai-tracing directory"
    exit 1
fi

# Check for ANTHROPIC_API_KEY
if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo "⚠️  Warning: ANTHROPIC_API_KEY not set"
    echo ""
    echo "Please set your Anthropic API key:"
    echo "  export ANTHROPIC_API_KEY='your-api-key-here'"
    echo ""
    read -p "Do you want to enter it now? (y/n) " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        read -p "Enter your Anthropic API key: " ANTHROPIC_API_KEY
        export ANTHROPIC_API_KEY
        echo "✓ API key set for this session"
    else
        echo "❌ Cannot run test without ANTHROPIC_API_KEY"
        exit 1
    fi
fi

# Check for KEYWORDSAI_API_KEY (optional)
if [ -z "$KEYWORDSAI_API_KEY" ]; then
    echo "ℹ️  Note: KEYWORDSAI_API_KEY not set (using test-key)"
    echo "   Set it to send traces to your KeywordsAI dashboard:"
    echo "   export KEYWORDSAI_API_KEY='your-keywordsai-key-here'"
    echo ""
fi

# Check if dependencies are installed
echo "📦 Checking dependencies..."
if [ ! -d "node_modules" ]; then
    echo "⚠️  node_modules not found. Installing dependencies..."
    npm install
else
    echo "✓ Dependencies already installed"
fi

# Check for required packages
echo ""
echo "📦 Checking required packages..."
MISSING_PACKAGES=()

if ! npm list @anthropic-ai/sdk &>/dev/null; then
    echo "⚠️  @anthropic-ai/sdk not installed"
    MISSING_PACKAGES+=("@anthropic-ai/sdk")
fi

if ! npm list @traceloop/instrumentation-anthropic &>/dev/null; then
    echo "⚠️  @traceloop/instrumentation-anthropic not installed"
    MISSING_PACKAGES+=("@traceloop/instrumentation-anthropic")
fi

if [ ${#MISSING_PACKAGES[@]} -gt 0 ]; then
    echo ""
    echo "Installing missing packages: ${MISSING_PACKAGES[*]}"
    npm install "${MISSING_PACKAGES[@]}"
    echo "✓ Packages installed"
fi

echo ""
echo "========================================="
echo "🚀 Running Anthropic Instrumentation Test"
echo "========================================="
echo ""

# Run the test
npm run test:anthropic

# Check exit code
if [ $? -eq 0 ]; then
    echo ""
    echo "========================================="
    echo "✅ Test completed successfully!"
    echo "========================================="
    echo ""
    echo "Next steps:"
    echo "  1. Check your KeywordsAI dashboard for traces"
    echo "  2. Verify token counts and cost metrics are present"
    echo "  3. Look for app name: 'anthropic-instrumentation-test'"
    echo ""
else
    echo ""
    echo "========================================="
    echo "❌ Test failed"
    echo "========================================="
    echo ""
    echo "Check the error messages above for details."
    echo ""
    exit 1
fi

