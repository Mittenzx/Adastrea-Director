# Adastrea Game Comment Library

## Overview

This library provides pre-defined blueprint comments specifically tailored for the Adastrea game development. These comments follow consistent styling and organization patterns to maintain clarity across all game blueprints.

## Color Scheme

Adastrea uses a consistent color scheme for comments:

| Category | Color | RGB | Hex | Use Case |
|----------|-------|-----|-----|----------|
| **Adastrea Brand** | Blue-Violet | (138, 43, 226) | #8A2BE2 | Game-specific systems |
| **Section Headers** | Cornflower Blue | (100, 149, 237) | #6495ED | Major sections |
| **Important** | Crimson | (220, 20, 60) | #DC143C | Critical notes |
| **TODO** | Gold | (255, 215, 0) | #FFD700 | Work in progress |
| **Bug/Issue** | Red-Orange | (255, 69, 0) | #FF4500 | Known issues |
| **Optimization** | Lime Green | (50, 205, 50) | #32CD32 | Performance notes |
| **Documentation** | Light Steel Blue | (176, 196, 222) | #B0C4DE | General docs |

## Comment Templates

### 1. Blueprint Header Comments

#### Standard Blueprint Header
```python
add_blueprint_comment(
    blueprint_path,
    """╔══════════════════════════════════════════╗
║        ADASTREA GAME BLUEPRINT        ║
║  Blueprint: BP_[Name]                     ║
║  System: [System Name]                    ║
║  Author: Adastrea Director                ║
║  Last Modified: [Date]                    ║
╚══════════════════════════════════════════╝""",
    position_x=0,
    position_y=-300,
    width=900,
    height=180,
    color=(138, 43, 226),  # Adastrea brand
    font_size=18
)
```

### 2. System-Specific Comments

#### Character System
```python
# Movement System
"""═══ ADASTREA CHARACTER MOVEMENT ═══
Handles player/NPC locomotion
- Walk/Run/Sprint speeds
- Jump mechanics
- Dash ability
- Stamina integration"""

# Combat System
"""═══ ADASTREA COMBAT SYSTEM ═══
Combat mechanics implementation
- Attack combos
- Weapon switching
- Damage calculation
- Hit detection"""

# Inventory System
"""═══ ADASTREA INVENTORY ═══
Item management system
- Item pickup/drop
- Equipment slots
- Weight system
- Quick access slots"""
```

#### World Systems
```python
# Quest System
"""═══ ADASTREA QUEST SYSTEM ═══
Quest tracking and management
- Quest objectives
- Progress tracking
- Reward distribution
- Quest log updates"""

# Dialogue System
"""═══ ADASTREA DIALOGUE ═══
NPC conversation system
- Dialogue trees
- Choice branches
- Relationship tracking
- Voice line triggers"""

# Economy System
"""═══ ADASTREA ECONOMY ═══
In-game currency and trading
- Currency management
- Shop interactions
- Price calculations
- Trade validation"""
```

#### Technical Systems
```python
# Save/Load System
"""═══ ADASTREA SAVE SYSTEM ═══
Game state persistence
- Save data structure
- Checkpoint system
- Cloud sync integration
- Auto-save logic"""

# Networking
"""═══ ADASTREA MULTIPLAYER ═══
Network replication logic
- Client prediction
- Server authority
- Lag compensation
- Sync points"""

# Performance
"""═══ ADASTREA OPTIMIZATION ═══
Performance-critical code
⚠️ Profiled and optimized
- Target: <2ms per frame
- LOD implementation
- Object pooling"""
```

### 3. Function Documentation Comments

#### Standard Function Comment
```python
"""╔═ FUNCTION: [FunctionName] ═╗
├─ Description: [What it does]
├─ Inputs:
│  ├─ [Input1]: [Type] - [Description]
│  └─ [Input2]: [Type] - [Description]
├─ Outputs:
│  └─ [Output]: [Type] - [Description]
├─ Side Effects: [If any]
└─ Adastrea Context: [Game-specific notes]
╚═══════════════════════════════╝"""
```

#### Example: Damage Calculation
```python
"""╔═ FUNCTION: CalculateAdastreaD amage ═╗
├─ Description: Calculates final damage with
│               Adastrea game modifiers
├─ Inputs:
│  ├─ BaseDamage: Float - Raw damage value
│  ├─ DamageType: Enum - Physical/Magical/Elemental
│  ├─ AttackerStats: Struct - Attacker attributes
│  └─ DefenderStats: Struct - Defender attributes
├─ Outputs:
│  └─ FinalDamage: Float - Modified damage value
├─ Side Effects: None
└─ Adastrea Context: Uses game-specific damage
                      formula with elemental affinities
╚════════════════════════════════════════════╝"""
```

### 4. Event Handler Comments

```python
# BeginPlay Events
"""▼ EVENT: BeginPlay
Adastrea initialization sequence
1. Load player stats
2. Initialize UI
3. Connect to game manager
4. Spawn starting equipment"""

# Input Events
"""▼ INPUT EVENT: Attack
Adastrea combat input handler
- Check stamina availability
- Validate combat state
- Trigger attack animation
- Apply damage on hit"""

# Collision Events
"""▼ COLLISION EVENT: OnHit
Adastrea damage interaction
- Identify hit actor type
- Calculate damage
- Apply effects
- Trigger VFX/SFX"""
```

### 5. Variable Group Comments

```python
# Player Stats
"""┌─ ADASTREA PLAYER STATS ─┐
│ Core character attributes  │
│ • Health (Current/Max)     │
│ • Stamina (Current/Max)    │
│ • Mana (Current/Max)       │
│ • Experience Points        │
│ • Character Level          │
└────────────────────────────┘"""

# Equipment Slots
"""┌─ ADASTREA EQUIPMENT ─┐
│ Wearable item slots    │
│ • Weapon (Main/Off)    │
│ • Armor (Head/Body)    │
│ • Accessories (Ring/Amulet) │
└────────────────────────┘"""

# Game Configuration
"""┌─ ADASTREA CONFIG ─┐
│ Game settings       │
│ • Difficulty Level  │
│ • Graphics Quality  │
│ • Audio Settings    │
└─────────────────────┘"""
```

### 6. State Machine Comments

```python
# Player State
"""╔═══ ADASTREA PLAYER STATE MACHINE ═══╗
║                                        ║
║  [Idle] → [Moving] → [Combat]        ║
║     ↓        ↓          ↓             ║
║  [Menu] ← [Inventory] ← [Dead]       ║
║                                        ║
╚════════════════════════════════════════╝"""

# AI Behavior
"""╔═══ ADASTREA AI STATE MACHINE ═══╗
║                                    ║
║  Patrol → Alert → Combat → Flee   ║
║     ↑        ↓       ↓       ↓     ║
║     └─────── Idle ───────────┘     ║
║                                    ║
╚════════════════════════════════════╝"""
```

### 7. TODO and Issue Comments

```python
# Standard TODO
"""📝 TODO - ADASTREA
Task: [Description]
Priority: [High/Medium/Low]
Assignee: [Name/Team]
Related Systems: [List]
Estimated Time: [Hours]
Dependencies: [If any]"""

# Bug Report
"""🐛 BUG - ADASTREA
Issue: [Description]
Severity: [Critical/High/Medium/Low]
Reproduction Steps:
1. [Step 1]
2. [Step 2]
Expected: [What should happen]
Actual: [What happens]
Workaround: [If available]"""

# Optimization Note
"""⚡ OPTIMIZATION - ADASTREA
Current: [Current implementation]
Issue: [Performance problem]
Target: [Performance goal]
Proposed: [Optimization approach]
Testing: [How to verify]"""
```

### 8. Integration Points

```python
# External System Integration
"""┌─ ADASTREA INTEGRATION ─┐
│ System: [External System] │
│ Purpose: [Why connected]  │
│ Data Flow: [Direction]    │
│ Dependencies: [List]      │
│ Contact: [Responsible]    │
└───────────────────────────┘"""

# API Endpoints
"""┌─ ADASTREA API ─┐
│ Endpoint: [URL/Function] │
│ Method: [GET/POST/etc]   │
│ Auth: [Required/None]    │
│ Response: [Format]       │
│ Rate Limit: [If any]     │
└──────────────────────────┘"""
```

### 9. Code Review Comments

```python
# Review Requested
"""👀 REVIEW REQUESTED - ADASTREA
Area: [Code section]
Concern: [What to review]
Questions:
1. [Question 1]
2. [Question 2]
Alternatives Considered: [List]
Decision Needed By: [Date]"""

# Performance Critical
"""⚠️ PERFORMANCE CRITICAL - ADASTREA
This code runs every frame!
- Profiled: [Yes/No]
- Target: [Time budget]
- Current: [Actual time]
- Optimizations: [Applied]"""
```

### 10. Documentation References

```python
# Design Document Reference
"""📖 ADASTREA DESIGN DOC
Document: [Doc name]
Section: [Section number/name]
Version: [Doc version]
Link: [URL if available]
Key Points:
• [Point 1]
• [Point 2]"""

# External Resource
"""🔗 ADASTREA RESOURCE
Type: [Tutorial/Forum/Asset]
Title: [Resource title]
Source: [Where to find]
Relevance: [Why included]
Last Checked: [Date]"""
```

## Quick Reference Functions

### Python API Usage

```python
from ue_python_api import UEPythonBridge

bridge = UEPythonBridge()

# Add Adastrea header
bridge.add_blueprint_comment(
    "/Game/Characters/BP_PlayerCharacter",
    "═══ ADASTREA CHARACTER SYSTEM ═══",
    position_y=-200,
    width=800,
    color=(138, 43, 226)
)

# Add function documentation
bridge.add_blueprint_comment(
    "/Game/Combat/BP_WeaponSystem",
    """Function: ProcessAdastreaAttack
    Handles Adastrea-specific attack logic""",
    position_x=100,
    position_y=100,
    width=500
)

# Add TODO
bridge.add_blueprint_comment(
    "/Game/UI/BP_MainMenu",
    "TODO: Integrate Adastrea save system",
    color=(255, 215, 0)
)
```

### MCP Tool Usage

```json
{
    "tool": "editor_add_blueprint_comment",
    "arguments": {
        "blueprint_path": "/Game/BP_GameMode",
        "comment_text": "═══ ADASTREA GAME MODE ═══\nCore game rules and initialization",
        "position_x": 0,
        "position_y": -300,
        "width": 800,
        "height": 120,
        "color": "adastrea"
    }
}
```

### CLI Usage

```bash
# Interactive
python unreal_mcp_cli.py
unreal> comment /Game/BP_Character "ADASTREA PLAYER" 0 -200

# Command-line
python unreal_mcp_cli.py add-comment \
    /Game/BP_Character \
    "ADASTREA COMBAT SYSTEM" \
    --x 0 --y -100 \
    --color adastrea
```

## Batch Comment Scripts

### Add Standard Headers to All Blueprints

```python
blueprints = [
    "/Game/Characters/BP_Player",
    "/Game/Characters/BP_Enemy",
    "/Game/Items/BP_Weapon",
    "/Game/UI/BP_HUD"
]

for bp in blueprints:
    bridge.add_blueprint_comment(
        bp,
        f"═══ ADASTREA GAME BLUEPRINT ═══\n{bp.split('/')[-1]}",
        position_y=-250,
        width=700,
        color=(138, 43, 226)
    )
```

### Add System Documentation

```python
systems = {
    "/Game/Combat": "Combat and damage calculation",
    "/Game/Movement": "Character locomotion",
    "/Game/Inventory": "Item management",
    "/Game/Quest": "Quest tracking and progression"
}

for path, description in systems.items():
    bridge.add_blueprint_comment(
        path,
        f"ADASTREA {path.split('/')[-1].upper()} SYSTEM\n{description}",
        position_y=-200,
        color=(100, 149, 237)
    )
```

## Style Guidelines

1. **Consistency**: Always use Adastrea branding in headers
2. **Clarity**: Make comments self-documenting
3. **Structure**: Use box drawing characters for visual organization
4. **Color Coding**: Follow the established color scheme
5. **Brevity**: Keep comments concise but complete
6. **Context**: Include game-specific details when relevant
7. **Updates**: Keep modification dates current

## Customization

To customize for specific Adastrea systems:

1. Identify your blueprint's purpose
2. Choose appropriate template from above
3. Replace placeholders with actual values
4. Adjust colors to match system category
5. Position comments logically in the graph

## Integration with Adastrea Director

All comment templates can be used with:
- **Python API** - Direct function calls
- **MCP Tools** - AI agent integration
- **CLI** - Command-line batch processing
- **Scripts** - Automated documentation generation

## Maintenance

- Review and update comments during code reviews
- Keep comment library in sync with game design docs
- Archive outdated templates
- Propose new templates as game systems evolve

## Conclusion

This comment library provides Adastrea-specific blueprint documentation patterns that:
- Maintain visual consistency across the project
- Facilitate team collaboration
- Support automated documentation
- Enable AI-assisted blueprint organization

Use these templates to keep Adastrea blueprints well-documented and easy to navigate!
