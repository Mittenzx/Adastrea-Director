# API Key Management Guide

This guide explains how to manage your API keys in Adastrea Director using the new secure local storage feature.

## Overview

Adastrea Director now supports secure local storage of API keys, eliminating the need to re-enter your keys after cloning the repository or starting a new session.

### Key Features

- **Persistent Storage**: Keys are stored in `~/.adastrea/config.json` (outside the repository)
- **Encryption**: Keys are encrypted using PBKDF2HMAC with machine-specific salt
- **Secure Permissions**: Config directory (700) and file (600) have secure permissions on Unix-like systems
- **Multiple Providers**: Supports Gemini and OpenAI API keys
- **Priority System**: Local config → Environment variables → .env file

## Quick Start

### Option 1: GUI (Recommended for beginners)

1. Launch the GUI:
   ```bash
   python gui_director.py
   ```

2. When prompted for an API key, enter it and check the box:
   - ☑ **"Save API key for future sessions"**

3. Click OK. Your key is now saved and will be automatically loaded in future sessions.

### Option 2: CLI (Recommended for advanced users)

```bash
# Save your API key
python main.py --set-api-key gemini

# You'll be prompted to enter your key (input is hidden)
Enter your GEMINI API key: ••••••••••••••••

✓ API key saved to /home/user/.adastrea/config.json
```

### Option 3: Environment Variables (Traditional method)

```bash
# For current session only
export GEMINI_KEY="your-api-key-here"

# Or for OpenAI
export OPENAI_API_KEY="your-api-key-here"
```

### Option 4: .env File (Repository-specific)

```bash
# Create .env file from example
cp .env.example .env

# Edit .env and add your key
nano .env

# Add this line:
GEMINI_KEY=your-api-key-here
```

## API Key Priority

The system checks for API keys in this order:

1. **Local Config** (`~/.adastrea/config.json`) - **Highest Priority**
2. **Environment Variables** (`GEMINI_KEY`, `OPENAI_API_KEY`)
3. **.env File** (in repository root)

This means if you have a key saved in local config, it will be used even if you also have an environment variable set.

## Managing Stored Keys

### View Configuration Status

```bash
python main.py --show-config
```

Output:
```
Configuration Status:
Location: /home/user/.adastrea/config.json
Exists: True

Stored API Keys:
  gemini: test-gem...2345
  openai: not set
```

### Save a New Key

```bash
# For Gemini
python main.py --set-api-key gemini

# For OpenAI
python main.py --set-api-key openai
```

### Update an Existing Key

Simply save a new key with the same provider name:

```bash
python main.py --set-api-key gemini
```

### Remove a Stored Key

```bash
# Remove Gemini key
python main.py --clear-api-key gemini

# Remove OpenAI key
python main.py --clear-api-key openai
```

### Clear All Configuration

To completely remove the config file:

```bash
rm ~/.adastrea/config.json
```

Or programmatically:

```python
import config_manager
config_manager.clear_all_config()
```

## Security Considerations

### How Keys Are Protected

1. **Encryption**: Keys are encrypted using PBKDF2HMAC with 100,000 iterations
2. **Machine-Specific**: The encryption key is derived from your username and hostname
3. **File Permissions**: On Unix-like systems:
   - Config directory: `700` (owner read/write/execute only)
   - Config file: `600` (owner read/write only)
4. **Outside Repository**: Config is stored in home directory, never committed to git

### What This Means

- **Portable Between Sessions**: Keys persist across repository clones and updates
- **Not Portable Between Machines**: Keys encrypted on one machine can't be decrypted on another
- **Not Portable Between Users**: Each user has their own config
- **Safe to Share Repository**: Config is in `.gitignore` and outside repo directory

### Best Practices

1. **Don't commit `.env` files** - Already in `.gitignore` but worth noting
2. **Rotate keys periodically** - Update your API keys from time to time
3. **Use different keys for different projects** - Keep your keys separate
4. **Revoke compromised keys immediately** - If a key is leaked, revoke it in the API provider's dashboard

## Troubleshooting

### Key Not Loading

If your stored key isn't being used:

1. **Check config exists**:
   ```bash
   python main.py --show-config
   ```

2. **Verify key is set**:
   ```bash
   python -c "import config_manager; print(config_manager.get_api_key('gemini'))"
   ```

3. **Check environment variable isn't overriding** (shouldn't happen, but just in case):
   ```bash
   echo $GEMINI_KEY
   ```

### Permission Errors

If you get permission errors:

```bash
# Fix directory permissions
chmod 700 ~/.adastrea

# Fix file permissions
chmod 600 ~/.adastrea/config.json
```

### Decryption Errors

If you move the config file between machines, decryption will fail. This is by design for security.

**Solution**: Re-enter your API key on the new machine:

```bash
python main.py --set-api-key gemini
```

### Config Location

**Default location**: `~/.adastrea/config.json`

On different platforms:
- **Linux/macOS**: `/home/username/.adastrea/config.json`
- **Windows**: `C:\Users\username\.adastrea\config.json`

## Advanced Usage

### Programmatic Access

You can use the config_manager module in your own scripts:

```python
import config_manager

# Save a key
config_manager.set_api_key("gemini", "your-api-key")

# Get a key
api_key = config_manager.get_api_key("gemini")
if api_key:
    print(f"Found key: {api_key[:8]}...")
else:
    print("No key found")

# Clear a key
config_manager.clear_api_key("gemini")

# Get config location
print(f"Config: {config_manager.get_config_location()}")
```

### Multiple API Keys

You can store keys for multiple providers:

```python
import config_manager

# Save keys for both providers
config_manager.set_api_key("gemini", "gemini-key-here")
config_manager.set_api_key("openai", "openai-key-here")

# Retrieve specific key
gemini_key = config_manager.get_api_key("gemini")
openai_key = config_manager.get_api_key("openai")
```

### Custom Configuration Storage

The config file is JSON and can store other settings too:

```python
import config_manager

# Load config
config = config_manager.load_config()

# Add custom settings
config["custom_setting"] = "value"
config["preferences"] = {
    "theme": "dark",
    "language": "en"
}

# Save config
config_manager.save_config(config)
```

**Note**: Only API keys are automatically encrypted. Custom settings are stored as plain text.

## Migration Guide

### From Environment Variables

If you're currently using environment variables:

1. Save your key to local config:
   ```bash
   python main.py --set-api-key gemini
   ```

2. (Optional) Remove the environment variable:
   ```bash
   unset GEMINI_KEY
   ```

3. (Optional) Remove from shell profile (`.bashrc`, `.zshrc`, etc.)

### From .env File

If you're using a `.env` file:

1. Note your current key:
   ```bash
   grep GEMINI_KEY .env
   ```

2. Save to local config:
   ```bash
   python main.py --set-api-key gemini
   ```

3. (Optional) Remove key from `.env` file:
   ```bash
   sed -i '/GEMINI_KEY/d' .env
   ```

## FAQ

### Q: Is my API key safe?

**A**: Yes. Keys are encrypted using industry-standard PBKDF2HMAC with 100,000 iterations, and the config file has secure permissions.

### Q: Can I use this on multiple machines?

**A**: Yes, but you'll need to enter the key on each machine separately. Keys are machine-specific for security.

### Q: What if I want to use different keys for different projects?

**A**: Use environment variables or `.env` files for project-specific keys. The local config is global to your user account.

### Q: Can I export my config to another machine?

**A**: No. Keys are encrypted with a machine-specific key for security. You'll need to re-enter them on the new machine.

### Q: How do I completely reset everything?

**A**: Remove the config file:
```bash
rm ~/.adastrea/config.json
```

### Q: Does this work on Windows?

**A**: Yes! The config is stored at `%USERPROFILE%\.adastrea\config.json`. File permissions are handled appropriately for each platform.

## Getting Your API Key

### Gemini API Key (Recommended)

1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Click "Create API Key"
3. Copy the key
4. Save it using `python main.py --set-api-key gemini`

**Free tier**: 1,500 requests/day (Flash), 50 requests/day (Pro)

### OpenAI API Key (Legacy)

1. Visit [OpenAI Platform](https://platform.openai.com/api-keys)
2. Click "Create new secret key"
3. Copy the key
4. Save it using `python main.py --set-api-key openai`

**Note**: OpenAI requires a paid account.

## Support

If you encounter issues:

1. Check this guide for troubleshooting steps
2. Run diagnostics: `python main.py --show-config`
3. Check file permissions: `ls -la ~/.adastrea/`
4. Open an issue on GitHub with details

---

**Last Updated**: 2024-11-14
