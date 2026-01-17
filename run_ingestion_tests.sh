#!/bin/bash
# Test runner script for RAG ingestion tests
#
# This script runs the comprehensive test suite for RAG ingestion simulation (22 tests)
#
# Usage:
#   ./run_ingestion_tests.sh          # Run all tests

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}======================================${NC}"
echo -e "${BLUE}RAG Ingestion Tests${NC}"
echo -e "${BLUE}======================================${NC}"
echo ""

# Check if pytest is installed
if ! python3 -m pytest --version &> /dev/null; then
    echo -e "${YELLOW}pytest not found. Installing pytest...${NC}"
    if ! pip install pytest pytest-mock --quiet; then
        echo -e "${RED}Error: Failed to install pytest. Please install manually with:${NC}"
        echo -e "${RED}  pip install pytest pytest-mock${NC}"
        exit 1
    fi
    echo -e "${GREEN}pytest installed successfully${NC}"
fi

echo -e "${GREEN}Running RAG Ingestion Simulation Tests (22 tests)${NC}"
echo ""

# Check if dependencies are installed
if ! python3 -c "import langchain" &> /dev/null; then
    echo -e "${YELLOW}Note: RAG tests require additional dependencies${NC}"
    echo -e "${YELLOW}Install with: pip install -r requirements.txt${NC}"
    echo ""
    exit 1
fi

python3 -m pytest tests/test_simulate_rag_ingestion.py -v --override-ini="addopts=" --tb=short

echo ""
echo -e "${BLUE}======================================${NC}"
echo -e "${GREEN}✓ Test execution complete!${NC}"
echo -e "${BLUE}======================================${NC}"
