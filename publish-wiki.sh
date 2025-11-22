#!/bin/bash
set -e

echo "🚀 Publishing Wiki to GitHub..."
echo ""

# Configuration
WIKI_DIR="wiki"
WIKI_REPO_URL="https://github.com/Mittenzx/Adastrea-Director.wiki.git"
TEMP_WIKI_DIR="/tmp/Adastrea-Director.wiki"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}Step 1: Checking prerequisites...${NC}"

# Check if wiki directory exists
if [ ! -d "$WIKI_DIR" ]; then
    echo -e "${RED}❌ Error: wiki/ directory not found${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Wiki directory found${NC}"

# Check if git is installed
if ! command -v git &> /dev/null; then
    echo -e "${RED}❌ Error: git is not installed${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Git is installed${NC}"

echo ""
echo -e "${BLUE}Step 2: Cloning wiki repository...${NC}"

# Remove temp directory if it exists
if [ -d "$TEMP_WIKI_DIR" ]; then
    echo "Removing existing temporary directory..."
    rm -rf "$TEMP_WIKI_DIR"
fi

# Clone the wiki repository
if git clone "$WIKI_REPO_URL" "$TEMP_WIKI_DIR"; then
    echo -e "${GREEN}✓ Wiki repository cloned${NC}"
else
    echo -e "${RED}❌ Error: Failed to clone wiki repository${NC}"
    echo ""
    echo "This might happen if:"
    echo "  1. The wiki hasn't been initialized yet"
    echo "  2. You don't have access to the repository"
    echo "  3. Authentication is required"
    echo ""
    echo "To initialize the wiki, visit:"
    echo "  https://github.com/Mittenzx/Adastrea-Director/wiki"
    echo "  and create the first page through the web interface."
    exit 1
fi

echo ""
echo -e "${BLUE}Step 3: Copying wiki content...${NC}"

# Copy all wiki content (excluding git directory)
rsync -av --delete "$WIKI_DIR/" "$TEMP_WIKI_DIR/" --exclude=".git" --exclude="README.md"

echo -e "${GREEN}✓ Content copied successfully${NC}"

echo ""
echo -e "${BLUE}Step 4: Committing changes...${NC}"

cd "$TEMP_WIKI_DIR"

# Configure git if not already configured
git config user.name "$(git config user.name 2>/dev/null || echo 'Wiki Publisher')"
git config user.email "$(git config user.email 2>/dev/null || echo 'wiki@adastrea.com')"

# Add all changes
git add .

# Check if there are changes to commit
if git diff --staged --quiet; then
    echo -e "${BLUE}ℹ️  No changes to commit - wiki is already up to date${NC}"
else
    # Commit changes
    COMMIT_MSG="Update wiki content ($(date +'%Y-%m-%d %H:%M:%S'))"
    git commit -m "$COMMIT_MSG"
    echo -e "${GREEN}✓ Changes committed${NC}"
    
    echo ""
    echo -e "${BLUE}Step 5: Pushing to GitHub...${NC}"
    
    # Push changes
    if git push; then
        echo -e "${GREEN}✓ Wiki published successfully!${NC}"
        echo ""
        echo -e "${GREEN}🎉 Your wiki is now live at:${NC}"
        echo "   https://github.com/Mittenzx/Adastrea-Director/wiki"
    else
        echo -e "${RED}❌ Error: Failed to push changes${NC}"
        echo ""
        echo "You may need to configure git credentials."
        echo "Changes are committed locally in: $TEMP_WIKI_DIR"
        echo ""
        echo "To push manually:"
        echo "  cd $TEMP_WIKI_DIR"
        echo "  git push"
        exit 1
    fi
fi

echo ""
echo -e "${BLUE}Cleaning up...${NC}"
cd -
# Optionally remove temp directory (commented out for safety)
# rm -rf "$TEMP_WIKI_DIR"
echo -e "${GREEN}✓ Done!${NC}"
echo ""
echo "Temporary wiki directory preserved at: $TEMP_WIKI_DIR"
echo "You can remove it manually if no longer needed."
