# Adastrea Director Wiki

This directory contains the source content for the [Adastrea Director Wiki](https://github.com/Mittenzx/Adastrea-Director/wiki).

## 📚 About This Directory

This `wiki/` directory serves as:
- **Source of Truth:** All wiki content is maintained here
- **Version Control:** Wiki content is tracked in the main repository
- **Staging Area:** Content is prepared here before being published to the GitHub Wiki
- **Backup:** Ensures wiki content is never lost

## 🏗️ Structure

```
wiki/
├── Home.md                    # Wiki homepage
├── README.md                  # This file
├── installation/              # Installation & setup guides
│   ├── Getting-Started.md
│   ├── Quick-Start.md
│   ├── System-Requirements.md
│   ├── Standalone-Setup.md
│   ├── Plugin-Setup.md
│   ├── Troubleshooting.md
│   └── FAQ.md
├── usage/                     # Usage guides
│   ├── Context-Aware-Assistant.md
│   ├── Planning-System.md
│   ├── Autonomous-Agents.md
│   ├── GUI-Application.md
│   └── Document-Ingestion.md
├── architecture/              # Architecture documentation
│   ├── System-Architecture.md
│   ├── Agent-Architecture.md
│   ├── Deployment-Modes.md
│   └── Data-Flow.md
├── phases/                    # Phase-specific documentation
│   ├── Phase-1-Foundation.md
│   ├── Phase-2-Planner.md
│   ├── Phase-3-Autonomous-Agents.md
│   └── Phase-4-Creative-Partner.md
├── development/               # Development guides
│   ├── Contributing.md
│   ├── Testing.md
│   ├── Code-Reference.md
│   └── Roadmap.md
├── design/                    # Design system
│   ├── Design-System.md
│   ├── Component-Library.md
│   └── UI-Guidelines.md
└── api/                       # API reference
    ├── Remote-Control-API.md
    └── Python-API.md
```

## 📖 How to Use This Wiki Content

### For Readers

Visit the [live wiki](https://github.com/Mittenzx/Adastrea-Director/wiki) to read the documentation with proper navigation and formatting.

### For Contributors

1. **Edit Files Locally:**
   - Clone the repository
   - Edit markdown files in the `wiki/` directory
   - Follow the [contribution guidelines](development/Contributing.md)

2. **Submit Changes:**
   - Create a branch
   - Make your changes
   - Submit a pull request
   - Changes will be synchronized to the GitHub Wiki after merge

3. **Sync to GitHub Wiki:**
   ```bash
   # Clone the wiki repository
   git clone https://github.com/Mittenzx/Adastrea-Director.wiki.git
   
   # Copy updated files
   cp -r wiki/* Adastrea-Director.wiki/
   
   # Commit and push
   cd Adastrea-Director.wiki
   git add .
   git commit -m "Update wiki content"
   git push
   ```

## ✍️ Writing Guidelines

### Markdown Standards

- Use standard GitHub Flavored Markdown
- Include a descriptive title (h1) at the top
- Use proper heading hierarchy (h1 → h2 → h3)
- Add code blocks with language specifiers
- Include navigation links at bottom of pages

### File Naming

- Use PascalCase with hyphens: `Getting-Started.md`
- Be descriptive but concise
- Match wiki page URLs

### Content Guidelines

1. **Start with Overview:** Brief introduction at the top
2. **Use Table of Contents:** For long pages (use anchors)
3. **Include Examples:** Show, don't just tell
4. **Add Navigation:** Link to related pages
5. **Keep Updated:** Update dates when content changes

### Link Format

**Internal Links (within wiki):**
```markdown
[Link Text](Page-Name.md)
[Link Text](../category/Page-Name.md)
```

**External Links (to repository):**
```markdown
[Link Text](https://github.com/Mittenzx/Adastrea-Director/blob/main/file.py)
```

**Cross-References:**
```markdown
See [Related Page](Related-Page.md) for more details.
```

## 🔄 Synchronization Process

### Manual Sync (Current)

1. Edit files in `wiki/` directory
2. Commit changes to main repository
3. Manually copy to wiki repository
4. Push to GitHub Wiki

### Automated Sync (Future)

A GitHub Action will automatically synchronize wiki content:
- Trigger: On push to main branch
- Action: Copy `wiki/` contents to wiki repository
- Result: Wiki always up-to-date

## 📝 Content Status

### ✅ Complete

- [x] Home page
- [x] Installation & Getting Started
- [x] Quick Start Tutorial
- [x] Context-Aware Assistant guide
- [x] System Architecture
- [x] Phase 1 documentation

### 🚧 In Progress

- [ ] Planning System guide (detailed)
- [ ] Autonomous Agents guide (detailed)
- [ ] All architecture pages
- [ ] All phase documentation
- [ ] Development guides
- [ ] Design system
- [ ] API reference

### 📋 Planned

- [ ] FAQ page
- [ ] Troubleshooting guide (expanded)
- [ ] Video tutorials
- [ ] Migration guides
- [ ] Best practices
- [ ] Performance optimization guide

## 🤝 Contributing to the Wiki

We welcome contributions to improve the documentation!

### How to Contribute

1. **Find or Create an Issue:**
   - Check existing [documentation issues](https://github.com/Mittenzx/Adastrea-Director/labels/documentation)
   - Create a new issue if needed

2. **Make Your Changes:**
   - Fork the repository
   - Edit files in `wiki/` directory
   - Follow writing guidelines above

3. **Submit a Pull Request:**
   - Clear description of changes
   - Link to related issue
   - Follow PR template

### What to Contribute

**Content:**
- New pages for missing topics
- Improvements to existing pages
- Code examples and tutorials
- Screenshots and diagrams

**Fixes:**
- Typos and grammar
- Broken links
- Outdated information
- Formatting issues

**Translations:**
- Translations to other languages (future)

## 📊 Wiki Metrics

- **Total Pages:** 20+ (growing)
- **Total Words:** 50,000+ (growing)
- **Categories:** 7 main sections
- **Last Updated:** 2025-11-22

## 🔗 Quick Links

- [Live Wiki](https://github.com/Mittenzx/Adastrea-Director/wiki)
- [Main Repository](https://github.com/Mittenzx/Adastrea-Director)
- [Issues](https://github.com/Mittenzx/Adastrea-Director/issues)
- [Discussions](https://github.com/Mittenzx/Adastrea-Director/discussions)

## 📞 Questions?

- **Documentation Issues:** [Create an issue](https://github.com/Mittenzx/Adastrea-Director/issues/new) with `documentation` label
- **General Questions:** Use [Discussions](https://github.com/Mittenzx/Adastrea-Director/discussions)
- **Contact Maintainer:** [@Mittenzx](https://github.com/Mittenzx)

---

**Thank you for helping improve Adastrea Director's documentation!** 📚

[View Live Wiki →](https://github.com/Mittenzx/Adastrea-Director/wiki)
