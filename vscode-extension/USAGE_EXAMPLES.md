# Copilot Integration Usage Examples

Quick reference guide for using @director in GitHub Copilot Chat.

## Basic Usage

### 1. Simple Question
```
@director What is the difference between Blueprints and C++ in Unreal Engine?
```

**Expected Response:**
- Detailed comparison
- Use cases for each
- Best practices
- When to use which approach

---

### 2. Generate Development Plan
```
@director /plan Create a third-person character with basic movement
```

**Expected Response:**
```markdown
## Development Plan

**Goal:** Create a third-person character with basic movement

### Tasks
1. Create Character C++ class
2. Set up Character Movement Component
3. Configure Input Bindings
4. Implement movement functions
5. Add camera components
6. Test in-game

### Steps
1. Create new C++ class: AMyCharacter inheriting from ACharacter
2. Add camera and spring arm components in constructor
3. Bind input in SetupPlayerInputComponent
...
```

---

### 3. Analyze Complexity
```
@director /analyze Implement AI pathfinding with dynamic obstacles
```

**Expected Response:**
```markdown
## Goal Analysis

**Summary:** Complex task requiring navigation system integration

**Complexity:** High

### Requirements
- Navigation mesh generation
- Dynamic obstacle detection
- Path recalculation
- Performance optimization

### Risks
- Performance issues with many obstacles
- Complex edge cases
- Memory overhead

### Recommendations
- Use UE's built-in Navigation System
- Implement obstacle avoidance
- Consider LOD for distant AI
```

---

### 4. Get Context
```
@director /context UCharacterMovementComponent
```

**Expected Response:**
```markdown
### UCharacterMovementComponent

Component for handling character movement, physics, and collision.

**Key Features:**
- Walking, falling, flying, swimming modes
- Network replication support
- Customizable movement parameters

**Common Methods:**
- SetWalkSpeed()
- LaunchCharacter()
- AddForce()
...
```

---

## Advanced Examples

### Code Review Workflow

**Step 1:** Select code in editor
```cpp
void AMyActor::Tick(float DeltaTime) {
    Super::Tick(DeltaTime);
    // Update logic every frame
    UpdatePosition();
    CheckCollisions();
    ProcessInput();
}
```

**Step 2:** Right-click → "Ask Director about this code"

**Step 3:** Ask: "How can I optimize this code?"

**Response:**
```markdown
## Optimization Suggestions

1. **Reduce Tick Frequency**
   - Use a timer instead of Tick
   - Only tick when necessary

2. **Disable Tick When Idle**
   - Set PrimaryActorTick.bCanEverTick = false when not needed

3. **Use Event-Driven Approach**
   - Replace polling with delegates/events

Example:
```cpp
// Instead of Tick
GetWorldTimerManager().SetTimer(
    TimerHandle, 
    this, 
    &AMyActor::UpdatePosition, 
    0.1f,  // Update every 0.1s instead of every frame
    true
);
```
```

---

### Feature Planning Workflow

**Step 1:** Initial Planning
```
@director /plan Create an inventory system
```

**Step 2:** Follow-up Analysis
```
@director /analyze Add item durability and repair mechanics to the inventory
```

**Step 3:** Get Implementation Context
```
@director /context How to implement item serialization in Unreal Engine
```

**Step 4:** Generate Code (using existing command)
```
Director: Generate and Apply Code
Goal: "Implement basic inventory system with durability"
```

---

## Real-World Scenarios

### Scenario 1: New to Unreal Engine

**Question 1:**
```
@director I'm new to Unreal. How do I create my first playable character?
```

**Question 2:**
```
@director /plan Create a player character that can walk, jump, and look around
```

**Question 3:**
```
@director What's the difference between Pawn and Character classes?
```

---

### Scenario 2: Debugging Issues

**Context:** You have a crash when spawning actors

**Question:**
```
@director Why might UWorld::SpawnActor return nullptr?
```

**Follow-up:**
```
@director How do I properly handle actor spawning failures?
```

---

### Scenario 3: Performance Optimization

**Context:** Game is running slowly

**Questions:**
```
@director /analyze Check performance of my game loop

@director What are common performance bottlenecks in Unreal Engine?

@director How do I profile my game to find slowdowns?
```

---

### Scenario 4: Learning Best Practices

**Code Selection:**
```cpp
UPROPERTY()
AActor* MyActor;  // Is this the right way?
```

**Action:** Right-click → "Get Director context"

**Response:**
```markdown
## UPROPERTY Best Practices

⚠️ Issue: Missing pointer safety specifier

**Recommended:**
```cpp
UPROPERTY()
TObjectPtr<AActor> MyActor;  // Modern approach (UE5+)

// Or with specifiers:
UPROPERTY(BlueprintReadOnly, Category = "My Category")
AActor* MyActor;
```

**Why:**
- TObjectPtr provides better nullptr safety
- UPROPERTY ensures garbage collection
- Specifiers control Blueprint exposure
```
```

---

## Comparison with Traditional Commands

### Old Way (Command Palette)
1. Ctrl+Shift+P
2. Type "Director: Ask Question"
3. Enter question
4. Check Output panel
5. No follow-ups

### New Way (Copilot Chat)
1. Open Copilot Chat
2. Type `@director your question`
3. Get formatted response in chat
4. Easy follow-ups
5. Suggested next steps

---

## Tips for Best Results

### 1. Be Specific
❌ `@director help`
✅ `@director How do I implement collision detection for a projectile?`

### 2. Use Appropriate Commands
- Use `/ask` for questions
- Use `/plan` for feature planning
- Use `/analyze` for complexity assessment
- Use `/context` for API documentation

### 3. Provide Context
```
@director I'm working on a multiplayer shooter. How should I implement hit detection?
```

Better than:
```
@director hit detection
```

### 4. Iterate and Follow Up
```
@director /plan Create a weapon system
@director /analyze Add weapon attachments and modding
@director Show me an example weapon class in C++
```

### 5. Combine with Commands
1. Plan in chat: `@director /plan ...`
2. Generate code: `Director: Generate and Apply Code`
3. Test: `Director: Run Tests`
4. Provide feedback: `Director: Provide Feedback`

---

## Common Patterns

### Pattern 1: Learn → Plan → Implement
```
1. @director What is the Actor Component pattern in UE?
2. @director /plan Create a health component for my character
3. Director: Generate and Apply Code
```

### Pattern 2: Debug → Understand → Fix
```
1. Select buggy code
2. Right-click → "Ask Director about this code"
3. Ask: "Why isn't this working?"
4. Apply suggested fix
```

### Pattern 3: Optimize → Measure → Improve
```
1. @director /analyze Current performance bottlenecks
2. @director How do I profile UE performance?
3. Apply optimizations
4. Director: Run Tests to verify
```

---

## Integration with Existing Workflows

### With Version Control
```
1. @director /plan New feature
2. Create feature branch
3. Director: Generate and Apply Code
4. Review changes: Director: Review Pending Changes
5. Commit approved changes
```

### With Testing
```
1. @director /plan Feature with tests
2. Director: Generate and Apply Code
3. Director: Run Tests
4. If failures: @director Why did these tests fail?
5. Fix and re-test
```

### With Documentation
```
1. Write code
2. Select function
3. Right-click → "Get Director context"
4. Use context to write documentation
5. @director Review my documentation for accuracy
```

---

## Keyboard Shortcuts

While @director doesn't have specific shortcuts, you can:

1. **Open Copilot Chat**: Check VS Code shortcuts
2. **Quick Chat**: Ctrl+Shift+I (inline chat)
3. **Command Palette**: Ctrl+Shift+P for Director commands

---

## Next Steps

After mastering these examples:

1. Read [COPILOT_INTEGRATION.md](COPILOT_INTEGRATION.md) for full documentation
2. Explore [PHASE2_GUIDE.md](PHASE2_GUIDE.md) for advanced features
3. Check [README.md](README.md) for complete feature list
4. Try Phase 2 features:
   - Automated code generation
   - Intelligent approval workflow
   - Automated testing
   - Feedback system

---

**Pro Tip:** The more context you provide, the better Director's responses!

**Remember:** Always verify AI-generated code and test thoroughly before production use.
