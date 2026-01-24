# API Key Configuration Guide

## Overview

As of this update, the Adastrea Director plugin now reads API keys directly from the `.env` file in your project root directory. This guide explains how to configure your API keys properly.

## Quick Start

1. **Create .env file**: In your Unreal Engine project root directory, create a file named `.env`
2. **Add your API key**: Add one of the following lines depending on your provider:
   ```
   GEMINI_API_KEY=your-actual-api-key-here
   ```
   or
   ```
   OPENAI_API_KEY=your-actual-api-key-here
   ```
3. **Restart Unreal Engine**: The plugin loads API keys at startup, so you must restart the editor
4. **Test the configuration**: Open Settings and click "Test API Key" to verify

## Supported Environment Variables

### For Google Gemini (Recommended)

The plugin checks these variables in priority order:
1. `GEMINI_API_KEY` (primary, recommended)
2. `GEMINI_KEY` (legacy support)
3. `GOOGLE_API_KEY` (fallback)

**Example `.env` file:**
```bash
# Gemini API Configuration
GEMINI_API_KEY=AIzaSyYourActualAPIKeyHere
LLM_PROVIDER=gemini
GEMINI_MODEL=gemini-1.5-flash
```

### For OpenAI

**Example `.env` file:**
```bash
# OpenAI API Configuration
OPENAI_API_KEY=sk-YourActualAPIKeyHere
LLM_PROVIDER=openai
```

## Getting API Keys

### Google Gemini API Key
1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Click "Get API Key"
3. Copy your key and add it to `.env`

### OpenAI API Key
1. Visit [OpenAI API Keys](https://platform.openai.com/api-keys)
2. Create a new API key
3. Copy your key and add it to `.env`

## Troubleshooting

### "No API key configured" error

**Symptom**: When clicking "Test API Key" in Settings, you see "No API key configured"

**Solution**:
1. Verify `.env` file exists in your project root (not in the Plugins folder)
2. Check that the API key variable name is correct (`GEMINI_API_KEY` or `OPENAI_API_KEY`)
3. Ensure there are no extra spaces around the `=` sign
4. **Restart Unreal Engine** - the plugin only loads keys at startup

### Query shows "Thinking..." indefinitely

**Symptom**: When you type a query, it shows "Thinking..." but never completes

**Possible Causes**:
1. **API key not configured**: Follow the steps above to add your API key
2. **Wrong provider selected**: Make sure the provider in Settings matches your API key
3. **Invalid API key**: Your key may have expired or been revoked
4. **Network issues**: Check your internet connection

**Solution**:
1. Open Settings and click "Test API Key"
2. If it shows an error, follow the error message instructions
3. Verify your internet connection is working
4. Try a simple query like "What is Unreal Engine?"

### Case sensitivity issues

The plugin now handles provider names case-insensitively. Both `gemini` and `Gemini` will work.

## Configuration File Locations

- **`.env` file**: Located in your Unreal Engine project root directory (same level as your .uproject file)
- **Plugin config**: `Saved/AdastreaDirector/config.ini` (stores non-sensitive settings)

## Security Best Practices

1. **Never commit `.env` files to version control**: Add `.env` to your `.gitignore`
2. **Use project-specific keys**: Don't share API keys between projects
3. **Rotate keys regularly**: Generate new API keys periodically
4. **Limit key permissions**: Use keys with minimum required permissions

## Example .env Template

You can copy `.env.example` to `.env` and fill in your values:

```bash
# Adastrea Director Configuration
# Copy this file to .env and add your actual API keys

# LLM Provider (gemini or openai)
LLM_PROVIDER=gemini

# Google Gemini API Key (get from: https://makersuite.google.com/app/apikey)
GEMINI_API_KEY=

# Or use OpenAI (get from: https://platform.openai.com/api-keys)
# OPENAI_API_KEY=

# Optional: Specific model to use
# GEMINI_MODEL=gemini-1.5-flash
# OPENAI_MODEL=gpt-4-turbo
```

## Changes from Previous Versions

**Before**: API keys could only be configured through Python backend
**Now**: Plugin reads keys directly from `.env` file at startup

**Benefits**:
- ✅ Immediate validation of API key presence
- ✅ Clear error messages when keys are missing
- ✅ "Test API Key" button works correctly
- ✅ Better user experience with helpful guidance

## Support

If you continue to experience issues:
1. Check the Output Log for detailed error messages
2. Verify all troubleshooting steps above
3. Ensure you're using the latest plugin version
4. See `TROUBLESHOOTING.md` for more help
