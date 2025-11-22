# Wiki Setup Guide

This document explains how to publish the wiki content from the `wiki/` directory to the GitHub Wiki.

## 📚 Overview

The `wiki/` directory contains all wiki content as markdown files. This content needs to be copied to the GitHub Wiki repository to be visible on https://github.com/Mittenzx/Adastrea-Director/wiki.

## 📊 Wiki Statistics

- **Total Pages:** 19 markdown files
- **Total Words:** ~15,000 words
- **Categories:** 8 sections
- **Status:** ✅ Complete and ready for publication

## 🗂️ Wiki Structure

```
wiki/
├── Home.md                           # Main entry point
├── README.md                         # Wiki documentation
├── _Sidebar.md                       # Navigation sidebar
├── _Footer.md                        # Footer for all pages
├── installation/                     # Installation guides (5 pages)
├── usage/                            # Usage guides (5 pages)
├── architecture/                     # Architecture docs (3 pages)
├── phases/                           # Phase documentation (1 page)
├── development/                      # Development guides (1 page)
├── design/                           # Design system (ready for content)
└── api/                              # API reference (ready for content)
```

## 🚀 Publishing to GitHub Wiki

### Prerequisites

- Git installed
- Write access to the Mittenzx/Adastrea-Director repository
- GitHub Wiki enabled for the repository

### Method 1: Manual Sync (One-Time Setup)

1. **Clone the wiki repository:**
   ```bash
   cd /tmp
   git clone https://github.com/Mittenzx/Adastrea-Director.wiki.git
   ```

2. **Copy wiki content:**
   ```bash
   # From the main repository directory
   cd /home/runner/work/Adastrea-Director/Adastrea-Director
   cp -r wiki/* /tmp/Adastrea-Director.wiki/
   ```

3. **Commit and push:**
   ```bash
   cd /tmp/Adastrea-Director.wiki
   git add .
   git commit -m "Initial wiki content - comprehensive documentation"
   git push
   ```

4. **Verify:**
   - Visit https://github.com/Mittenzx/Adastrea-Director/wiki
   - Check that all pages are visible
   - Test navigation links

### Method 2: Sync Script

Create a sync script for regular updates:

```bash
#!/bin/bash
# sync-wiki.sh

set -e

WIKI_DIR="wiki"
WIKI_REPO="/tmp/Adastrea-Director.wiki"
WIKI_URL="https://github.com/Mittenzx/Adastrea-Director.wiki.git"

echo "📚 Syncing wiki content..."

# Clone or update wiki repo
if [ ! -d "$WIKI_REPO" ]; then
    echo "Cloning wiki repository..."
    git clone "$WIKI_URL" "$WIKI_REPO"
else
    echo "Updating wiki repository..."
    cd "$WIKI_REPO"
    git pull
    cd -
fi

# Copy wiki content
echo "Copying wiki files..."
rsync -av --delete "$WIKI_DIR/" "$WIKI_REPO/" --exclude=".git"

# Commit and push
cd "$WIKI_REPO"
if [ -n "$(git status --porcelain)" ]; then
    echo "Committing changes..."
    git add .
    git commit -m "Update wiki content - $(date +%Y-%m-%d)"
    git push
    echo "✅ Wiki synced successfully!"
else
    echo "ℹ️  No changes to sync"
fi
```

Make it executable:
```bash
chmod +x sync-wiki.sh
```

Run it:
```bash
./sync-wiki.sh
```

### Method 3: GitHub Action (Automated)

Create `.github/workflows/sync-wiki.yml`:

```yaml
name: Sync Wiki

on:
  push:
    branches:
      - main
    paths:
      - 'wiki/**'
  workflow_dispatch:

jobs:
  sync:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout main repository
        uses: actions/checkout@v3

      - name: Checkout wiki repository
        uses: actions/checkout@v3
        with:
          repository: Mittenzx/Adastrea-Director.wiki
          path: wiki-repo
          token: ${{ secrets.GITHUB_TOKEN }}

      - name: Copy wiki content
        run: |
          rsync -av --delete wiki/ wiki-repo/ --exclude=".git" --exclude="README.md"
          
      - name: Commit and push
        run: |
          cd wiki-repo
          git config user.name "GitHub Actions"
          git config user.email "actions@github.com"
          git add .
          git diff --quiet && git diff --staged --quiet || (git commit -m "Auto-sync wiki content" && git push)
```

## 📝 Maintaining the Wiki

### Making Changes

1. **Edit locally:**
   ```bash
   # Edit files in wiki/ directory
   vim wiki/installation/Getting-Started.md
   ```

2. **Test locally:**
   ```bash
   # Preview markdown files
   # Or use a markdown preview tool
   ```

3. **Commit to main repository:**
   ```bash
   git add wiki/
   git commit -m "docs: update getting started guide"
   git push
   ```

4. **Sync to wiki:**
   ```bash
   ./sync-wiki.sh
   # Or wait for GitHub Action (if configured)
   ```

### Adding New Pages

1. **Create the file:**
   ```bash
   # Create in appropriate directory
   touch wiki/usage/New-Feature.md
   ```

2. **Add content:**
   ```markdown
   # New Feature Guide
   
   Content here...
   
   ---
   
   [← Back to Usage](Context-Aware-Assistant.md)
   ```

3. **Update navigation:**
   - Add to `_Sidebar.md` if needed
   - Add links from related pages

4. **Sync to wiki:**
   ```bash
   ./sync-wiki.sh
   ```

### Updating Existing Pages

1. **Edit the file** in `wiki/` directory
2. **Update "Last updated" date** at bottom
3. **Commit changes**
4. **Sync to wiki**

## 🔗 Link Format

### Internal Links (Wiki Pages)

Use relative paths without `.md` extension:

```markdown
[Getting Started](installation/Getting-Started)
[System Architecture](../architecture/System-Architecture)
```

### External Links (Repository)

Use full GitHub URLs:

```markdown
[View Code](https://github.com/Mittenzx/Adastrea-Director/blob/main/main.py)
```

## 📋 Checklist for Publishing

Before publishing to GitHub Wiki:

- [ ] All pages have proper titles (h1)
- [ ] Navigation links work (test locally)
- [ ] Code examples are formatted correctly
- [ ] Internal links use correct format
- [ ] _Sidebar.md is complete
- [ ] _Footer.md is set
- [ ] No TODO/WIP sections in published pages
- [ ] Dates are current

## 🔍 Verification After Publishing

After syncing to GitHub Wiki:

1. **Check homepage:**
   - Visit https://github.com/Mittenzx/Adastrea-Director/wiki
   - Verify Home page loads correctly

2. **Test navigation:**
   - Click links in sidebar
   - Verify all pages load
   - Check no broken links

3. **Test search:**
   - Use wiki search function
   - Verify results are relevant

4. **Check formatting:**
   - Code blocks render correctly
   - Images display (if any)
   - Tables are formatted

5. **Mobile view:**
   - Check wiki on mobile device
   - Verify navigation works

## 🐛 Troubleshooting

### Issue: "Wiki not found"

**Solution:**
- Ensure GitHub Wiki is enabled in repository settings
- Go to Settings → Features → Enable Wikis

### Issue: "Access denied when pushing"

**Solution:**
```bash
# Use SSH instead of HTTPS
git clone git@github.com:Mittenzx/Adastrea-Director.wiki.git
```

Or configure credentials:
```bash
git config --global credential.helper store
```

### Issue: "Links broken after publishing"

**Solution:**
- Check link format (no `.md` extension for wiki links)
- Use relative paths correctly
- GitHub Wiki automatically converts `.md` links

### Issue: "Sidebar not showing"

**Solution:**
- Ensure `_Sidebar.md` is in root of wiki repo
- Check formatting (should be simple markdown list)
- GitHub Wiki has character limit on sidebar (~4KB)

## 📚 Resources

- [GitHub Wiki Documentation](https://docs.github.com/en/communities/documenting-your-project-with-wikis)
- [Markdown Guide](https://www.markdownguide.org/)
- [Wiki Template](wiki/Home.md)

## 🎯 Next Steps

After initial publish:

1. **Announce to team:** Share wiki URL with team members
2. **Add to README:** Link to wiki in main README
3. **Set up automation:** Implement GitHub Action for auto-sync
4. **Monitor feedback:** Watch for issues or questions
5. **Iterate:** Continuously improve based on feedback

## 📞 Support

Need help with wiki setup?

- **Documentation:** [Wiki README](wiki/README.md)
- **Issues:** [Create an issue](https://github.com/Mittenzx/Adastrea-Director/issues)
- **Discussions:** [Ask in discussions](https://github.com/Mittenzx/Adastrea-Director/discussions)

---

**Wiki is ready to publish!** 🎉

Last updated: 2025-11-22
