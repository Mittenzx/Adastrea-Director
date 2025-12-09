# GitHub Copilot Integration Guide

## Overview

The Adastrea Director VS Code extension now includes full integration with GitHub Copilot Chat, providing AI-powered assistance for Unreal Engine development directly within your IDE.

**Phase 1 (Weeks 3-4): Copilot Integration** - ✅ **COMPLETE**

## Features

### 1. Chat Participant (@director)

Interact with Director's RAG system through GitHub Copilot Chat using the `@director` participant.

#### Basic Usage

Open Copilot Chat and type:
```
@director How do I create a player character in Unreal Engine?
```

The Director will provide answers based on:
- Unreal Engine documentation
- Your project-specific context
- Best practices and patterns
- RAG-powered knowledge base

### 2. Slash Commands

Use specialized slash commands for different types of queries:

#### `/ask` - General Questions (Default)
```
@director /ask What is the difference between Blueprints and C++?
```

#### `/plan` - Development Planning
```
@director /plan Create a health system with regeneration
```

Generates a structured development plan with:
- Task breakdown
- Implementation steps
- Considerations and best practices

#### `/analyze` - Goal Analysis
```
@director /analyze Implement AI pathfinding with dynamic obstacles
```

Provides detailed analysis including:
- Complexity assessment
- Requirements
- Potential risks
- Recommendations

#### `/context` - Context Retrieval
```
@director /context Blueprint event graph execution order
```

Retrieves relevant context from Director's RAG system.

#### `/help` - Show Help
```
@director /help
```

Displays available commands and usage examples.

### 3. Code Actions

Right-click on selected code to access Director commands:

#### Ask Director about this code
- Select code in the editor
- Right-click and choose "Ask Director about this code"
- Enter your question
- View the answer in the Output panel

#### Get Director context
- Select code in the editor
- Right-click and choose "Get Director context"
- View detailed context and documentation in a side panel

### 4. Hover Context (Optional)

Hover over Unreal Engine symbols (classes starting with U, A, F, E, T) to see Director-powered documentation.

**Supported symbols:**
- `UObject` - Base class for all UE objects
- `AActor` - Base class for actors
- `FVector` - 3D vector structure
- `ECollisionChannel` - Collision channel enum
- And more...

## Configuration

### Enable/Disable Features

Configure Copilot integration in VS Code settings:

```json
{
  "director.copilot.enabled": true,
  "director.copilot.enableHoverContext": true,
  "director.copilot.enableCodeActions": true
}
```

### Settings Reference

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `director.copilot.enabled` | boolean | `true` | Enable GitHub Copilot Chat integration |
| `director.copilot.enableHoverContext` | boolean | `true` | Show Director context on hover |
| `director.copilot.enableCodeActions` | boolean | `true` | Enable Director code actions |

## Prerequisites

### Required

1. **VS Code 1.80.0 or higher**
2. **Director IPC Server running** on port 5555
   ```bash
   python Plugins/AdastreaDirector/Python/ipc_server.py --port 5555
   ```
3. **Connected to Director** via `Director: Connect to Unreal Engine`

### Optional

4. **GitHub Copilot Extension** for enhanced experience
   - Install from: https://marketplace.visualstudio.com/items?itemName=GitHub.copilot
5. **GitHub Copilot Chat Extension**
   - Install from: https://marketplace.visualstudio.com/items?itemName=GitHub.copilot-chat

## Example Workflows

### Workflow 1: Learning Unreal Engine API

1. Open a C++ file in your Unreal Engine project
2. Hover over a class name (e.g., `AActor`)
3. See Director's documentation in the hover tooltip
4. Click "Ask Director about this code" for more details

### Workflow 2: Planning a Feature

1. Open Copilot Chat
2. Type: `@director /plan Create an inventory system`
3. Review the generated plan
4. Follow up with: `@director /analyze Add item durability`
5. Use the plan to guide implementation

### Workflow 3: Code Review and Context

1. Select a function or code block
2. Right-click → "Get Director context"
3. Review documentation, examples, and best practices
4. Apply suggestions to improve your code

### Workflow 4: Quick Questions

1. Open Copilot Chat
2. Type: `@director What's the best way to handle player input?`
3. Get an immediate answer from Director's RAG system
4. Follow up with: `@director Show me an example`

## Advanced Features

### Context-Aware Responses

Director uses your project context when providing answers:
- Current file and language
- Surrounding code
- Project structure
- Unreal Engine version (if configured)

### Follow-up Suggestions

After each response, Director provides relevant follow-up actions:
- 🔨 Generate Code
- 🔍 Analyze
- 📋 Create Plan
- 📖 More Details
- 💡 Example

### Integration with Other Commands

Combine Copilot Chat with other Director commands:

1. Use `@director /plan` to create a plan
2. Run `Director: Generate and Apply Code` to implement
3. Run `Director: Run Tests` to validate
4. Provide feedback via `Director: Provide Feedback`

## Troubleshooting

### Chat Participant Not Available

**Problem:** `@director` doesn't appear in Copilot Chat

**Solutions:**
1. Ensure VS Code version is 1.80.0 or higher
2. Check that the extension is activated
3. Reload VS Code window (`Developer: Reload Window`)
4. Check Output panel for initialization errors

### Connection Issues

**Problem:** "Not connected to Director" message in chat

**Solutions:**
1. Start the Director IPC server
2. Run `Director: Connect to Unreal Engine`
3. Check connection status in the status bar
4. Run `Director: Run Connection Diagnostics`

### Hover Context Not Showing

**Problem:** No context appears when hovering over symbols

**Solutions:**
1. Enable hover context: `"director.copilot.enableHoverContext": true`
2. Ensure you're hovering over Unreal Engine symbols (U*, A*, F*, etc.)
3. Connect to Director first
4. Check that the file is C++ or C

### Code Actions Missing

**Problem:** Right-click menu doesn't show Director options

**Solutions:**
1. Enable code actions: `"director.copilot.enableCodeActions": true`
2. Reload VS Code window
3. Ensure you have text selected
4. Check supported file types (C++, TypeScript, JavaScript)

## API Reference

### Chat Participant

```typescript
interface DirectorChatParticipant {
  id: 'director.chat'
  name: 'director'
  commands: ['ask', 'plan', 'analyze', 'context', 'help']
}
```

### Commands

| Command | Arguments | Description |
|---------|-----------|-------------|
| `director.askAboutSelection` | document, range | Ask about selected code |
| `director.getContextForSelection` | document, range | Get context for selection |

## Best Practices

### 1. Be Specific

❌ `@director help with code`
✅ `@director How do I implement collision detection for a projectile?`

### 2. Use Appropriate Commands

- Use `/ask` for general questions
- Use `/plan` for feature planning
- Use `/analyze` for complexity assessment
- Use `/context` for API documentation

### 3. Provide Context

When asking about code:
- Select relevant code snippets
- Mention your Unreal Engine version
- Specify your goal or problem

### 4. Iterate

Follow up on responses:
```
@director /plan Create a save system
@director /analyze Add cloud save support
@director Show me an example of serialization
```

### 5. Combine with Commands

- Generate plans in chat
- Apply code via commands
- Test using Director commands
- Provide feedback for learning

## Limitations

### Current Limitations

1. **Connection Required**: Must be connected to Director IPC server
2. **Language Support**: Best results with C++ and Blueprint-related queries
3. **Context Window**: Limited by IPC protocol capabilities
4. **Response Time**: Depends on Director RAG query performance

### Future Enhancements

Planned for future releases:
- Real-time code completion suggestions
- Inline code generation
- Multi-file context awareness
- Blueprint visual scripting support
- Performance profiling integration

## Support

### Getting Help

1. Check the [main README](README.md) for general extension documentation
2. Review [troubleshooting](#troubleshooting) section
3. Run `Director: Run Connection Diagnostics`
4. Check Output panel: "Adastrea Director" channel
5. Enable debug mode: `Director: Toggle Debug Mode`

### Reporting Issues

When reporting Copilot integration issues, include:
- VS Code version
- Extension version
- GitHub Copilot extension version (if installed)
- Error messages from Output panel
- Steps to reproduce

## Examples Gallery

### Example 1: Creating a Character

```
@director /plan Create a third-person character with basic movement
```

**Response:**
```markdown
## Development Plan

**Goal:** Create a third-person character with basic movement

### Tasks
1. Create Character C++ class inheriting from ACharacter
2. Set up Character Movement Component
3. Configure Input Bindings
4. Implement movement functions
5. Add camera and spring arm components
6. Test in-game

### Steps
1. Create new C++ class: `AMyCharacter`
2. Add camera components in constructor...
```

### Example 2: Understanding API

```
@director /context UCharacterMovementComponent
```

**Response:**
```markdown
### UCharacterMovementComponent

Component for handling character movement, physics, and collision.

**Key Features:**
- Walking, falling, flying, swimming modes
- Network replication support
- Physics integration
- Customizable movement parameters
...
```

### Example 3: Code Review

Select this code:
```cpp
void AMyActor::Tick(float DeltaTime) {
    Super::Tick(DeltaTime);
    // Heavy computation here
}
```

Ask: `@director How can I optimize this Tick function?`

**Response:**
```markdown
To optimize your Tick function:

1. **Reduce Tick Frequency**: Use a timer instead
2. **Disable Tick When Not Needed**: Set bCanEverTick = false
3. **Move to Event-Driven**: Use events instead of polling
...
```

## Changelog

### v0.3.0 - Copilot Integration

**Added:**
- ✅ GitHub Copilot Chat participant (@director)
- ✅ Slash commands (ask, plan, analyze, context, help)
- ✅ Code actions for selected code
- ✅ Hover context for Unreal Engine symbols
- ✅ Context provider for RAG integration
- ✅ Configuration options for Copilot features

**Completed:**
- ✅ Phase 1, Weeks 3-4: Copilot Integration
- ✅ Context retrieval from Director RAG system
- ✅ Command palette commands for Director queries
- ✅ Code generation with Director context

## Resources

- [GitHub Copilot Documentation](https://docs.github.com/copilot)
- [VS Code Chat API](https://code.visualstudio.com/api/extension-guides/ai/chat)
- [Adastrea Director Repository](https://github.com/Mittenzx/Adastrea-Director)
- [Unreal Engine Documentation](https://docs.unrealengine.com/)

---

*Part of the Adastrea Director VS Code Extension - Phase 1 Complete* ✅
