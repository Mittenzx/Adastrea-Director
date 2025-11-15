# GUI Settings Guide

## Overview

The Adastrea Director GUI now includes a comprehensive settings dialog that allows you to configure various aspects of the application. This guide explains all available settings and how to use them.

## Accessing Settings

There are two ways to open the settings dialog:

1. **Menu Bar**: Click `Edit` → `Settings...`
2. **Keyboard Shortcut**: Press `Ctrl+,` (Ctrl + Comma)

## Settings Sections

### 1. API Keys

Configure your API keys for different LLM providers.

#### LLM Provider Selection

Choose which Large Language Model provider to use:

- **Gemini (Recommended)**: Google's Gemini API
  - 73% cheaper than GPT-3.5
  - Excellent quality
  - Generous free tier
  - Get your key at: https://makersuite.google.com/app/apikey

- **OpenAI**: OpenAI's GPT models
  - Industry-standard quality
  - Wider model selection
  - Requires paid account for most features

#### API Key Configuration

**Gemini API Key**:
- Enter your Gemini API key
- The key is masked with bullet points (•) for security
- Keys are encrypted and stored securely in `~/.adastrea/config.json`

**OpenAI API Key**:
- Enter your OpenAI API key
- Only required if using OpenAI as the LLM provider
- Also encrypted and stored securely

#### Embedding Provider

Choose which provider to use for document embeddings:

- **HuggingFace (Free)**: 
  - Completely free, no API key required
  - Works offline after initial model download
  - Good quality for most use cases
  - **Recommended for most users**

- **OpenAI**: 
  - Higher quality embeddings
  - Requires OpenAI API key
  - Incurs API usage costs
  - Better for production use cases

### 2. Display Settings

Customize the visual appearance of the application.

#### Default Font Size

- **Range**: 8pt to 20pt
- **Default**: 10pt
- **Description**: Sets the default font size for the conversation text
- **Note**: You can still adjust font size on-the-fly using the A+/A- buttons

#### Auto-save Settings

- **Default**: Enabled
- **Description**: Automatically saves your settings when you click "Save"
- **Storage**: Settings are stored in `~/.adastrea/config.json`

#### Show Timestamps

- **Default**: Enabled
- **Description**: Shows timestamps (HH:MM:SS) for each message in the conversation
- **Benefits**: 
  - Track when messages were sent
  - Useful for debugging and logging
  - Helps identify conversation flow

## Keyboard Shortcuts

The settings dialog supports keyboard shortcuts:

- **Enter**: Save settings
- **Escape**: Cancel without saving
- **Ctrl+,**: Open settings (from main window)

## Saving Settings

Click the **Save** button to apply and save all settings. Settings are:

1. **Applied immediately** to the current session
2. **Saved to disk** in `~/.adastrea/config.json`
3. **Encrypted** for security (API keys)
4. **Persistent** across application restarts

## Settings Storage

Settings are stored in a secure, encrypted format:

- **Location**: `~/.adastrea/config.json`
- **Encryption**: API keys are encrypted with machine-specific key
- **Format**: JSON
- **Permissions**: User-only access (600 on Unix systems)

### Example Settings File Structure

```json
{
  "llm_provider": "gemini",
  "embedding_provider": "huggingface",
  "display": {
    "font_size": 10,
    "show_timestamps": true,
    "auto_save": true
  },
  "api_keys": {
    "gemini": "<encrypted>",
    "openai": "<encrypted>"
  }
}
```

## Best Practices

### Security

1. **Never share your API keys** with anyone
2. **Don't commit** API keys to version control
3. **Use separate keys** for development and production
4. **Rotate keys regularly** if they may have been exposed

### Performance

1. **Use HuggingFace embeddings** for offline work
2. **Use Gemini** for the best cost/performance ratio
3. **Use OpenAI** only if you need specific GPT models

### Usability

1. **Enable auto-save** to avoid losing settings
2. **Keep timestamps on** for better conversation tracking
3. **Adjust font size** to your comfort level
4. **Save different API keys** for different projects

## Troubleshooting

### Settings Not Saving

**Problem**: Settings don't persist after restart

**Solutions**:
- Check that `~/.adastrea/` directory exists and is writable
- Verify auto-save is enabled
- Manually click "Save" before closing
- Check file permissions on config file

### API Key Not Working

**Problem**: API key shows as invalid

**Solutions**:
- Verify the key is correct (copy-paste from provider)
- Check that you've selected the correct provider
- Ensure the key has proper permissions on the provider's dashboard
- Try regenerating the key

### Settings Dialog Not Opening

**Problem**: Settings dialog doesn't appear

**Solutions**:
- Check if another dialog is already open
- Try using keyboard shortcut (Ctrl+,)
- Check error messages in console
- Restart the application

## Migration from Previous Versions

If you're upgrading from a previous version:

1. **Old API keys** are automatically detected and migrated
2. **Settings format** is updated automatically
3. **No manual intervention** required in most cases

### Manual Migration

If automatic migration fails:

1. Note your old API key (from environment variables or .env)
2. Open Settings dialog
3. Enter your API key
4. Select your preferred providers
5. Click Save

## Related Documentation

- [GUI Quick Start](GUI_QUICK_START.md) - Getting started with the GUI
- [GUI Improvements](GUI_IMPROVEMENTS.md) - All GUI features
- [Keyboard Shortcuts](GUI_QUICK_START.md#keyboard-shortcuts) - Complete shortcut reference

## Support

If you encounter issues with settings:

1. Check this documentation
2. Review error messages in the status bar
3. Check the conversation history for system messages
4. Open an issue on GitHub with details

---

**Last Updated**: 2025-11-15  
**Version**: 1.0.0
