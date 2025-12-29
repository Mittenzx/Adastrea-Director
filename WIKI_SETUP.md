# Wiki Setup Guide (Reference)

> **✅ Wiki is Live!** This guide is now a reference document. The wiki has been published and is actively maintained at https://github.com/Mittenzx/Adastrea-Director/wiki

This document explains how to publish wiki content from the `wiki/` directory to the GitHub Wiki.

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

### Method 1: Automated Script (Easiest) ⭐

**NEW:** Use the provided `publish-wiki.sh` script for one-click publishing:

```bash
# Make sure you're in the repository root
cd /home/runner/work/Adastrea-Director/Adastrea-Director

# Run the publish script
./publish-wiki.sh
```

The script will:
- ✅ Clone the wiki repository
- ✅ Copy all wiki content
- ✅ Commit changes with timestamp
- ✅ Push to GitHub Wiki
- ✅ Provide clear success/error messages

**Note:** The wiki must be initialized first. If you get an error, visit https://github.com/Mittenzx/Adastrea-Director/wiki and create the first page through the web interface, then run the script again.

### Method 2: GitHub Actions (Fully Automated) 🤖

**NEW:** A GitHub Actions workflow will automatically sync wiki content when you push changes to the `wiki/` directory on the main branch.

**Manual Trigger:**
1. Go to [Actions](https://github.com/Mittenzx/Adastrea-Director/actions)
2. Select "Publish Wiki" workflow
3. Click "Run workflow"
4. Optionally add a custom commit message
5. Click "Run workflow" button

The workflow will automatically:
- Copy wiki content to the wiki repository
- Commit and push changes
- Report success/failure in the workflow summary

### Method 3: Manual Sync

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

### Method 4: Alternative Manual Script

If you prefer, you can create a custom sync script. The repository now includes `publish-wiki.sh` which handles this automatically (see Method 1).

For reference, here's a minimal sync script:

```bash
#!/bin/bash
# Custom sync script example
set -e

WIKI_DIR="wiki"
WIKI_REPO="/tmp/Adastrea-Director.wiki"
WIKI_URL="https://github.com/Mittenzx/Adastrea-Director.wiki.git"

# Clone if needed
[ ! -d "$WIKI_REPO" ] && git clone "$WIKI_URL" "$WIKI_REPO"

# Copy and push
rsync -av --delete "$WIKI_DIR/" "$WIKI_REPO/" --exclude=".git" --exclude="README.md"
cd "$WIKI_REPO"
git add . && git commit -m "Update wiki - $(date +%Y-%m-%d)" && git push || echo "No changes"
```

**Note:** A GitHub Actions workflow (`.github/workflows/publish-wiki.yml`) is now included in the repository. It will automatically run when you push changes to the `wiki/` directory on the main branch, or you can trigger it manually as described in Method 2 above.

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
