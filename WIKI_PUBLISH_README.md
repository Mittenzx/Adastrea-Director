# Quick Wiki Publishing Guide (Reference)

> **✅ Wiki is Published!** The wiki is live at https://github.com/Mittenzx/Adastrea-Director/wiki. This guide is maintained as a reference for future wiki updates.

This repository includes automated tools to easily publish wiki content updates to GitHub Wiki.

## 🚀 Quick Start - Easiest Method

Simply run the publish script:

```bash
./publish-wiki.sh
```

This will automatically:
- Clone the wiki repository
- Copy all content from `wiki/` directory
- Commit and push to GitHub Wiki
- Show you the results

## 🤖 Automated Publishing

A GitHub Actions workflow is configured to automatically publish wiki changes:

### Automatic Trigger
- Pushes to `main` branch that modify `wiki/**` files will auto-publish

### Manual Trigger
1. Go to [Actions](https://github.com/Mittenzx/Adastrea-Director/actions)
2. Select "Publish Wiki" workflow
3. Click "Run workflow"

## 📚 View the Wiki

After publishing, view your wiki at:
https://github.com/Mittenzx/Adastrea-Director/wiki

## 🔧 Troubleshooting

### First Time Setup

If the script fails with "wiki repository not found":

1. Visit https://github.com/Mittenzx/Adastrea-Director/wiki
2. Click "Create the first page" 
3. Add any content (e.g., "Wiki coming soon")
4. Save the page
5. Run `./publish-wiki.sh` again

This initializes the wiki repository, after which automated publishing will work.

### Authentication Issues

If you get authentication errors:
- Ensure you have write access to the repository
- Check that GitHub CLI (`gh`) is authenticated, or
- Set up SSH keys for GitHub

## 📖 More Information

For detailed documentation, see:
- [WIKI_SETUP.md](WIKI_SETUP.md) - Complete setup and maintenance guide
- [wiki/README.md](wiki/README.md) - Wiki content documentation

---

**Need help?** Check the [FAQ](wiki/installation/FAQ.md) or [create an issue](https://github.com/Mittenzx/Adastrea-Director/issues).
