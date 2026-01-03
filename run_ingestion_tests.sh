#!/bin/bash
# Test runner script for RAG and GUI Director ingestion tests
#
# This script runs the comprehensive test suites for:
# 1. RAG ingestion simulation (22 tests)
# 2. GUI Director ingestion simulation (17 tests)
#
# Usage:
#   ./run_ingestion_tests.sh          # Run all tests
#   ./run_ingestion_tests.sh gui      # Run only GUI tests
#   ./run_ingestion_tests.sh rag      # Run only RAG tests

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}======================================${NC}"
echo -e "${BLUE}RAG & GUI Director Ingestion Tests${NC}"
echo -e "${BLUE}======================================${NC}"
echo ""

# Determine which tests to run
TEST_SUITE="${1:-all}"

# Check if pytest is installed
if ! python3 -m pytest --version &> /dev/null; then
    echo -e "${YELLOW}Installing pytest...${NC}"
    pip install pytest pytest-mock --quiet
fi

case "$TEST_SUITE" in
    "gui")
        echo -e "${GREEN}Running GUI Director Ingestion Tests (17 tests)${NC}"
        echo ""
        python3 -m pytest tests/test_gui_director_ingestion.py -v --override-ini="addopts=" --tb=short
        ;;
    
    "rag")
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
        ;;
    
    "all")
        echo -e "${GREEN}Running GUI Director Tests (17 tests)${NC}"
        echo ""
        python3 -m pytest tests/test_gui_director_ingestion.py -v --override-ini="addopts=" --tb=short
        
        echo ""
        echo -e "${BLUE}--------------------------------------${NC}"
        echo ""
        
        # Try to run RAG tests if dependencies are available
        if python3 -c "import langchain" &> /dev/null; then
            echo -e "${GREEN}Running RAG Ingestion Tests (22 tests)${NC}"
            echo ""
            python3 -m pytest tests/test_simulate_rag_ingestion.py -v --override-ini="addopts=" --tb=short
        else
            echo -e "${YELLOW}Skipping RAG tests - dependencies not installed${NC}"
            echo -e "${YELLOW}Install with: pip install -r requirements.txt${NC}"
        fi
        ;;
    
    *)
        echo "Usage: $0 [all|gui|rag]"
        exit 1
        ;;
esac

echo ""
echo -e "${GREEN}✓ Test execution complete!${NC}"
