#!/bin/bash
#
# Quick Ingestion Script for Adastrea Game Repository
#
# This script simplifies the process of ingesting the Mittenzx/Adastrea game
# repository documentation into the RAG system for plugin testing.
#
# Prerequisites:
# 1. Python 3.9-3.12 installed
# 2. Dependencies installed: pip install -r requirements.txt
# 3. Internet access (required for HuggingFace model download on first run)
#
# Usage:
#   ./quick_ingest_game.sh
#
# The script will:
# 1. Clone the Adastrea game repository (public, no token needed)
# 2. Ingest documentation from Docs/, Source/, and Content/ directories
# 3. Create a ChromaDB database in ./chroma_db_adastrea/
# 4. Use HuggingFace embeddings (no API key required, runs locally)
#
# For plugin testing:
# - The plugin should be configured to use the same database path
# - Collection name: adastrea_game_docs
# - Database path: ./chroma_db_adastrea (relative to project root)

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${CYAN}🎮 Adastrea Game Repository - Quick Ingestion${NC}"
echo ""

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: python3 is not installed${NC}"
    echo "Please install Python 3.9-3.12"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1-2)
echo -e "${GREEN}✓ Python $PYTHON_VERSION found${NC}"

# Check if dependencies are installed
echo -e "${CYAN}Checking dependencies...${NC}"
if ! python3 -c "import langchain_community" 2>/dev/null; then
    echo -e "${YELLOW}⚠ Dependencies not installed${NC}"
    echo "Installing dependencies..."
    if [ -f requirements.txt ]; then
        pip install -r requirements.txt
    else
        echo -e "${RED}Error: requirements.txt not found in the current directory${NC}"
        echo "Please ensure requirements.txt is present and re-run this script."
        exit 1
    fi
fi
echo -e "${GREEN}✓ Dependencies OK${NC}"

# Check internet connectivity (required for first-time HuggingFace model download)
echo -e "${CYAN}Checking internet connectivity...${NC}"
if ping -c 1 huggingface.co &> /dev/null; then
    echo -e "${GREEN}✓ Internet connection OK${NC}"
else
    echo -e "${YELLOW}⚠ Cannot reach huggingface.co${NC}"
    echo -e "${YELLOW}  First-time setup requires internet access to download the embedding model${NC}"
    echo -e "${YELLOW}  Subsequent runs will use the cached model${NC}"
    echo ""
    echo "Options:"
    echo "1. Connect to internet and run again"
    echo "2. Use OpenAI embeddings instead:"
    echo "   export EMBEDDING_PROVIDER=openai"
    echo "   export OPENAI_API_KEY=your-key-here"
    echo "   ./quick_ingest_game.sh"
    echo ""
    read -p "Continue anyway? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Run ingestion
echo ""
echo -e "${CYAN}Starting ingestion...${NC}"
echo "This may take several minutes depending on the size of the documentation."
echo ""

python3 ingest_game_repo.py \
    --collection-name adastrea_game_docs \
    --persist-dir ./chroma_db_adastrea

# Check if ingestion was successful
if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}✅ Ingestion complete!${NC}"
    echo ""
    echo "Database location: ./chroma_db_adastrea"
    echo "Collection name: adastrea_game_docs"
    echo ""
    echo "To test with the plugin:"
    echo "1. Configure the plugin to use database path: ./chroma_db_adastrea"
    echo "2. Configure the plugin to use collection: adastrea_game_docs"
    echo "3. Test queries in the plugin UI"
    echo ""
    echo "To view statistics:"
    echo "  python3 ingest_game_repo.py --stats"
else
    echo ""
    echo -e "${RED}✗ Ingestion failed${NC}"
    echo "Check the error messages above for details"
    exit 1
fi
