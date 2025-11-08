# Adastrea Director GUI - Quick Start Guide

## Getting Started in 3 Easy Steps

### 1. Launch the GUI
```bash
python gui_director.py
```

### 2. Set Your API Key
- Click the **🔑 Set API Key** button (or press `Ctrl+K`)
- Enter your OpenAI API key
- Press Enter or click OK

### 3. Start Asking Questions!
- Type your question in the input field
- Press Enter (or click **Ask ▶**)
- Get instant AI-powered answers about your game development project

---

## Quick Reference

### Main Buttons

| Button | Action | Shortcut |
|--------|--------|----------|
| 📚 Update Knowledge Base | Load project documents | `Ctrl+U` |
| 🔑 Set API Key | Configure OpenAI API | `Ctrl+K` |
| 🗑️ Clear | Clear conversation | `Ctrl+L` |
| 📋 Copy | Copy last response | Menu: `Ctrl+C` |
| **Ask ▶** | Submit question | `Enter` |

### Keyboard Shortcuts

#### Most Used
- **Enter** or **Ctrl+Enter** - Send your question
- **Ctrl+K** - Set/change API key
- **Ctrl+L** - Clear conversation and start fresh

#### File Operations
- **Ctrl+E** - Export conversation to file
- **Alt+F4** - Exit application

#### Text Controls
- **A-** button - Decrease font size
- **A+** button - Increase font size

### Menu Bar Quick Access

#### File Menu
- Export Conversation... (`Ctrl+E`)
- Exit

#### Edit Menu
- Copy Response (`Ctrl+C`)
- Clear Conversation (`Ctrl+L`)
- Set API Key (`Ctrl+K`)

#### Help Menu
- Keyboard Shortcuts
- About

---

## Common Tasks

### First Time Setup

1. **Launch the GUI**
   ```bash
   python gui_director.py
   ```

2. **Set API Key** (will auto-prompt)
   - Enter your OpenAI API key when prompted
   - Or click 🔑 button later

3. **Load Your Documents** (optional but recommended)
   - Click **📚 Update Knowledge Base**
   - Wait for processing to complete

4. **Start Chatting**
   - Type a question about your game project
   - Press Enter

### During Development

#### Ask a Question
1. Type your question in the input field
2. Press Enter or click **Ask ▶**
3. View the response in the conversation area

#### Copy an Answer
1. After getting a response
2. Click **📋 Copy** button
3. Paste into your documentation or code

#### Export a Conversation
1. Click **File** → **Export Conversation...**
2. Choose location and filename
3. Save as .txt or .md file

#### Start Fresh
1. Click **🗑️ Clear** button (or `Ctrl+L`)
2. Conversation resets with welcome message
3. Start asking new questions

### Tips for Best Results

#### Update Knowledge Base Regularly
- Click **📚 Update Knowledge Base** whenever you:
  - Add new documentation
  - Update game design documents
  - Create new code files
  - Modify project structure

#### Ask Clear, Specific Questions
**Good Questions:**
- "What are the player's quantum abilities?"
- "How should I implement the phase shift mechanic?"
- "What performance requirements are specified?"

**Less Effective:**
- "Tell me about the game"
- "What's this about?"
- "Help"

#### Use Conversation History
- Scroll up to review previous answers
- Ask follow-up questions
- AI remembers conversation context

#### Adjust Font for Comfort
- Use **A-** / **A+** buttons to adjust text size
- Settings apply immediately
- Range: 8pt to 20pt

---

## Troubleshooting

### "No documents found in database"
**Solution:** Update the knowledge base
1. Click **📚 Update Knowledge Base**
2. Wait for processing
3. Try your question again

### "API Key Error"
**Solution:** Set or update your API key
1. Click **🔑 Set API Key** (or `Ctrl+K`)
2. Enter a valid OpenAI API key
3. Click OK

### GUI Won't Start
**Check:** Python and tkinter installation
```bash
# Test tkinter
python -c "import tkinter; tkinter.Tk()"
```

If error, install tkinter:
- **Ubuntu/Debian**: `sudo apt-get install python3-tk`
- **macOS**: Included with Python installer
- **Windows**: Included with Python

### Response Too Small/Large
**Solution:** Adjust font size
- Click **A-** to decrease
- Click **A+** to increase
- Or use menu: adjust window size

---

## Features Overview

### Conversation History
- All questions and answers saved
- Timestamped entries
- Color-coded by role:
  - Your questions in **cyan**
  - AI responses in **orange**
  - System messages in **gray**
  - Errors in **red**

### Copy & Export
- **Copy**: Get last response on clipboard
- **Export**: Save entire conversation to file
  - Includes all Q&A pairs
  - Timestamps preserved
  - Choose .txt or .md format

### Visual Feedback
- Status bar shows current operation
- Emoji indicators:
  - ✓ = Ready
  - 🤔 = Processing
  - ❌ = Error
- Buttons disable during operations

### Accessibility
- High contrast dark theme
- Adjustable font size (8-20pt)
- Full keyboard navigation
- Tooltips on hover
- Screen reader friendly

---

## Example Workflow

### Planning a New Feature

1. **Ask about existing design**
   ```
   You: "What gameplay mechanics are currently specified?"
   ```

2. **Get implementation advice**
   ```
   You: "How should I implement the quantum tunneling ability?"
   ```

3. **Check requirements**
   ```
   You: "What are the performance constraints for abilities?"
   ```

4. **Export for reference**
   - Click File → Export Conversation
   - Save as "quantum_feature_planning.txt"

5. **Clear and continue**
   - Press `Ctrl+L` to clear
   - Start planning next feature

### Debugging Help

1. **Describe the problem**
   ```
   You: "The phase shift animation is stuttering at 30 FPS"
   ```

2. **Ask for suggestions**
   ```
   You: "What are the recommended optimization techniques?"
   ```

3. **Copy the solution**
   - Click **📋 Copy**
   - Paste into your notes or code comments

### Documentation Review

1. **Update knowledge base**
   - Click **📚 Update Knowledge Base**

2. **Verify understanding**
   ```
   You: "Summarize the core gameplay loop"
   ```

3. **Check consistency**
   ```
   You: "Are there any conflicts in the ability descriptions?"
   ```

---

## Best Practices

### 1. Keep API Key Secure
- Don't share your API key
- Don't commit it to version control
- Set it fresh each session if needed

### 2. Update Knowledge Base
- Before major development sessions
- After updating documentation
- When adding new features

### 3. Use Keyboard Shortcuts
- Faster than clicking
- More efficient workflow
- Less context switching

### 4. Export Important Conversations
- Design discussions
- Implementation decisions
- Problem-solving sessions

### 5. Organize Questions
- One topic per conversation
- Clear when switching topics
- Export before clearing

---

## Learn More

- **Full Feature List**: See [GUI_IMPROVEMENTS.md](GUI_IMPROVEMENTS.md)
- **Visual Guide**: See [GUI_VISUAL_COMPARISON.md](GUI_VISUAL_COMPARISON.md)
- **Visual Description**: See [GUI_SCREENSHOT_DESCRIPTION.md](GUI_SCREENSHOT_DESCRIPTION.md)
- **Project Overview**: See [README.md](README.md)

---

## Getting Help

### In the GUI
- Click **Help** → **Keyboard Shortcuts**
- Click **Help** → **About**
- Tooltips on all buttons (hover to see)

### Documentation
- Read the welcome message
- Check the README
- Review improvement docs

### Common Issues
- Most issues solved by updating knowledge base
- Check API key if queries fail
- Restart GUI if it becomes unresponsive

---

## Welcome Message Reference

When you first start the GUI, you'll see:

```
🤖 Welcome to Adastrea Director!

Your AI-powered game development assistant is ready to help.

Getting Started:
1. Set your OpenAI API Key (🔑 button or Ctrl+K)
2. Update the knowledge base with your project docs (📚 button or Ctrl+U)
3. Ask questions about your game design, code, or documentation

Try asking:
• "What is the main gameplay loop?"
• "Describe the player abilities"
• "How should I implement the quantum phase mechanic?"

Keyboard Shortcuts:
• Enter or Ctrl+Enter - Send question
• Ctrl+L - Clear conversation
• Ctrl+C - Copy last response
• Ctrl+K - Set API key
• Ctrl+U - Update knowledge base

Type your question below to get started! 🚀
```

---

**Remember**: The AI assistant is here to help with your game development. Ask questions, explore ideas, and get instant answers based on your project documentation!

Happy developing! 🎮✨
