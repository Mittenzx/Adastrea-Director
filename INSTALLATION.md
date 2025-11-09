# Installation Guide for Adastrea Director

This guide provides detailed installation instructions for different platforms and helps resolve common dependency issues.

## Prerequisites

- **Python 3.9 or higher** (Python 3.12+ recommended for best compatibility)
- **pip** package manager
- **git** (for cloning the repository)

## Standard Installation

### 1. Clone the Repository

```bash
git clone https://github.com/Mittenzx/Adastrea-Director.git
cd Adastrea-Director
```

### 2. Create a Virtual Environment (Recommended)

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Upgrade pip

```bash
pip install --upgrade pip
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Set Up API Keys

```bash
# Create a .env file or export environment variable
export OPENAI_API_KEY="your-api-key-here"
```

## Platform-Specific Installation

### 🍎 macOS (Apple Silicon - M1/M2/M3/M4)

Apple Silicon Macs may encounter issues with `onnxruntime` (required by ChromaDB). Here are the solutions:

#### Option 1: Use Rosetta 2 (Recommended for Compatibility)

```bash
# Install Python via Homebrew with x86_64 architecture
arch -x86_64 /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
arch -x86_64 brew install python@3.12

# Create virtual environment with x86_64 Python
arch -x86_64 /usr/local/bin/python3.12 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

#### Option 2: Use Native ARM with onnxruntime-silicon

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install all dependencies except chromadb first
pip install numpy>=2.0.0,<3.0.0 pandas>=2.2.0,<3.0.0
pip install langchain>=0.3.19,<0.4.0
pip install langchain-openai>=0.3.0,<0.4.0  
pip install langchain-community>=0.3.27,<0.4.0
pip install openai>=1.57.0,<2.0.0
pip install pypdf>=5.1.0,<6.0.0 python-docx>=1.1.0,<2.0.0
pip install markdown>=3.7,<4.0.0 beautifulsoup4>=4.12.3,<5.0.0
pip install sentence-transformers>=3.3.0,<4.0.0
pip install tiktoken>=0.8.0,<1.0.0
pip install click>=8.1.7,<9.0.0 python-dotenv>=1.0.1,<2.0.0
pip install rich>=13.9.4,<14.0.0 pydantic>=2.10.3,<3.0.0

# Install onnxruntime-silicon (Apple Silicon optimized)
pip install onnxruntime-silicon>=1.14.0

# Now install chromadb
pip install chromadb>=0.5.23,<0.6.0
```

#### Option 3: Use Docker (Universal Solution)

```bash
# Pull and run using Docker
docker pull chromadb/chroma
docker run -p 8000:8000 chromadb/chroma

# In another terminal, modify the code to use remote ChromaDB
# See "Using Remote ChromaDB Server" section below
```

### 🐧 Linux

#### Standard Linux (x86_64)

The standard installation should work without issues:

```bash
pip install -r requirements.txt
```

#### Linux ARM (Raspberry Pi, ARM servers)

```bash
# Install build dependencies
sudo apt-get update
sudo apt-get install -y python3-dev build-essential cmake

# Install dependencies
pip install -r requirements.txt

# If onnxruntime fails, build from source:
pip install --no-binary onnxruntime onnxruntime>=1.14.1
```

If building from source fails, consider using Docker as described in the macOS Option 3.

### 🪟 Windows

#### Standard Windows Installation

```bash
# Using Command Prompt or PowerShell
python -m venv venv
venv\Scripts\activate

# Upgrade pip
python -m pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt
```

**⚠️ Important for Windows 11 Users:**

If you get the error `Could not find a version that satisfies the requirement onnxruntime` on Windows 11 x86_64:

**Most Common Cause: Python Version Incompatibility**

Check your Python version:
```bash
python --version
```

**Solutions:**

1. **If you have Python 3.13+**: onnxruntime doesn't support Python 3.13 yet. You need Python 3.12 or lower.
   - Download and install Python 3.12 from [python.org](https://www.python.org/downloads/)
   - Create a new virtual environment with Python 3.12
   - Retry installation

2. **If you have Python 3.12 or lower and still get the error**:
   ```bash
   # Upgrade pip and setuptools
   python -m pip install --upgrade pip setuptools wheel
   
   # Try installing with verbose output to see the issue
   pip install --verbose onnxruntime
   
   # If that fails, try installing from a specific index
   pip install --index-url https://pypi.org/simple/ onnxruntime
   ```

3. **Check for network/proxy issues**:
   ```bash
   # Test PyPI connectivity
   python -m pip install --upgrade pip
   
   # If behind a proxy, configure pip
   pip config set global.proxy http://your-proxy:port
   ```

4. **Last resort - Use Docker**:
   ```bash
   docker pull chromadb/chroma
   docker run -p 8000:8000 chromadb/chroma
   # See "Using Remote ChromaDB Server" section below
   ```

#### Windows ARM (Surface devices with ARM processors)

Similar to Linux ARM, you may need to build onnxruntime from source or use the Docker approach.

## Troubleshooting

### Issue: `Could not find a version that satisfies the requirement onnxruntime`

**Common Causes**:
1. **Python version incompatibility** (most common on Windows 11)
2. **Platform lacks pre-built wheels** (ARM systems)
3. **Network/proxy issues**

**Solutions by Platform**:

**Windows 11 (x86_64)**:
1. **Check Python version**: `python --version`
   - If Python 3.13+: Install Python 3.12 or lower (onnxruntime doesn't support 3.13 yet)
   - If Python 3.8 or lower: Upgrade to Python 3.9-3.12
2. **Upgrade pip**: `python -m pip install --upgrade pip setuptools wheel`
3. **Test connectivity**: `pip install --verbose onnxruntime` to see detailed error
4. **Use Docker** as fallback (see Windows section above)

**macOS Apple Silicon**:
1. **Use Rosetta 2** - See macOS Option 1 above
2. **Use onnxruntime-silicon** - See macOS Option 2 above  

**Linux/Windows ARM**:
1. **Build from source**:
   ```bash
   pip install --no-binary onnxruntime onnxruntime>=1.14.1
   ```
2. **Use Docker** - See Option 3 above

### Issue: `numpy` version conflicts

**Cause**: Some packages require numpy 2.0+ while others are incompatible.

**Solution**: The requirements.txt already specifies compatible versions. Ensure you're using Python 3.12+ for best compatibility.

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Issue: Import errors after installation

**Cause**: Virtual environment issues or incomplete installation.

**Solution**:
```bash
# Deactivate and recreate virtual environment
deactivate
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### Issue: `sentence-transformers` installation fails

**Cause**: Missing system dependencies for PyTorch.

**Solution** (Linux):
```bash
sudo apt-get install -y python3-dev build-essential
pip install torch --index-url https://download.pytorch.org/whl/cpu
pip install -r requirements.txt
```

## Using Remote ChromaDB Server

If you cannot install chromadb locally, you can use a remote ChromaDB server:

### 1. Start ChromaDB Server

```bash
# Using Docker
docker pull chromadb/chroma
docker run -p 8000:8000 chromadb/chroma

# Or using pip (if onnxruntime works on your server)
pip install chromadb
chroma run --host 0.0.0.0 --port 8000
```

### 2. Modify Connection Settings

Update your code to connect to the remote server instead of using local persistence:

```python
# In main.py or ingest.py, modify the Chroma initialization:

# OLD (local persistence):
vectorstore = Chroma(
    collection_name=self.collection_name,
    embedding_function=self.embeddings,
    persist_directory=self.persist_directory,
)

# NEW (remote server):
import chromadb
from chromadb.config import Settings

client = chromadb.HttpClient(
    host="localhost",  # or your server IP
    port=8000,
    settings=Settings()
)

vectorstore = Chroma(
    client=client,
    collection_name=self.collection_name,
    embedding_function=self.embeddings,
)
```

## Verification

After installation, verify everything works:

```bash
# Run compatibility check
python check_compatibility.py

# Run validation
python validate_requirements.py

# Test the application
python main.py
```

## Getting Help

If you continue to experience issues:

1. **Check your Python version**: `python --version` (should be 3.9+)
2. **Check your platform**: `uname -m` (x86_64, arm64, etc.)
3. **Check pip version**: `pip --version` (should be 20.0+)
4. **Review error messages** carefully - they often indicate the specific issue
5. **Open an issue** on GitHub with:
   - Your platform and Python version
   - Full error message
   - Output of `pip list`

## Alternative: Pre-configured Development Environment

For the easiest setup experience, consider using:

- **GitHub Codespaces**: One-click cloud development environment
- **Docker**: Fully containerized environment
- **Cloud IDEs**: Replit, Google Colab, etc.

These platforms provide pre-configured environments where all dependencies work out of the box.
