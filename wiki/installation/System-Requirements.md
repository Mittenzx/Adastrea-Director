# System Requirements

Minimum and recommended requirements for Adastrea Director.

## Minimum Requirements

### Hardware
- **CPU:** 2+ cores
- **RAM:** 4GB minimum
- **Storage:** 2GB free space
- **Network:** Internet connection (for cloud LLMs and initial setup)

### Software
- **Python:** 3.9 or higher
- **pip:** Package manager (included with Python)

### Operating Systems
- **Windows:** 10 or higher
- **macOS:** 10.14 (Mojave) or higher
- **Linux:** Ubuntu 20.04+ or equivalent

## Recommended Requirements

### Hardware
- **CPU:** 4+ cores
- **RAM:** 8GB or more
- **Storage:** 5GB+ free space (for document databases)
- **GPU:** CUDA-compatible GPU (optional, for faster embeddings)

### Software
- **Python:** 3.12 or higher (best compatibility)
- **Git:** For cloning the repository

## Optional Requirements

### For GPU Acceleration
- **NVIDIA GPU:** CUDA-compatible
- **CUDA Toolkit:** 11.0 or higher
- **cuDNN:** Compatible version

### For Unreal Engine Plugin
- **Unreal Engine:** 5.0 or higher
- **Visual Studio:** 2019 or higher (Windows)
- **Xcode:** 12.0 or higher (macOS)

### For Local LLM (Ollama)
- **RAM:** 16GB+ recommended
- **Storage:** 10GB+ for models

## Platform-Specific Notes

### Windows
- Visual C++ Build Tools may be required for some dependencies
- Git Bash or WSL recommended for best experience

### macOS
- Apple Silicon (M1/M2) supported with Rosetta 2
- Xcode Command Line Tools required

### Linux
- build-essential and python3-dev packages recommended
- X11 or Wayland for GUI

## API Requirements

### LLM Providers (choose one)
- **Google Gemini:** API key (free tier available)
- **OpenAI:** API key (pay-per-use)
- **Ollama:** Local installation (no API key)

### Embeddings (optional)
- **Default:** HuggingFace (no API key needed)
- **Optional:** OpenAI embeddings API key

---

[← Back to Installation](Getting-Started.md)
