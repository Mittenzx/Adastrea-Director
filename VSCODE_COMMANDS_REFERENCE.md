# VSCode Remote Control Commands - Complete Reference

## Overview

The Adastrea Director VSCode extension now includes **over 160+ Unreal Engine commands** accessible through the Command Palette. Commands are organized into categories for easy discovery.

## Quick Command Picker

**Command:** `Adastrea: Quick Command Picker`

The fastest way to access all commands. Opens an interactive picker with:
- **160+ commands** organized by category
- **Search/filter** by name, category, or description
- **Visual icons** for each category
- **Command preview** showing what will be executed

**Categories:**
- Performance Stats (16 commands)
- Debug & Profiling (10 commands)
- Rendering (15 commands)
- Gameplay (10 commands)
- Assets & Content (6 commands)
- Networking (4 commands)
- Audio (2 commands)
- Build & Compile (3 commands)
- Console (4 commands)

## Command Categories

### Performance Stats (16 commands)

Monitor performance metrics in real-time.

| Command | Description |
|---------|-------------|
| `Adastrea: Show FPS Stats` | Display frames per second |
| `Adastrea: Show Unit Stats` | Frame time breakdown (Game/Draw/GPU) |
| `Adastrea: Show GPU Stats` | GPU performance metrics |
| `Adastrea: Show Memory Stats` | Memory usage by category |
| `Adastrea: Show Streaming Stats` | Texture/asset streaming info |
| `Adastrea: Show Engine Stats` | Core engine metrics |
| `Adastrea: Show Game Stats` | Game-specific performance |
| `Adastrea: Show Scene Rendering Stats` | Scene rendering breakdown |
| `Adastrea: Show RHI Stats` | Rendering Hardware Interface stats |
| `Adastrea: Show Level Stats` | Level streaming status |
| `Adastrea: Show Particle Stats` | Particle system performance |
| `Adastrea: Show Physics Stats` | Physics simulation metrics |
| `Adastrea: Show AI Stats` | AI system performance |
| `Adastrea: Show Animation Stats` | Animation system metrics |

**Console Commands:**
- `stat fps` - FPS counter
- `stat unit` - Frame time breakdown
- `stat gpu` - GPU stats
- `stat memory` - Memory usage
- `stat streaming` - Streaming info
- `stat engine` - Engine metrics
- `stat game` - Game stats
- `stat scenerendering` - Scene rendering
- `stat rhi` - RHI stats
- `stat levels` - Level streaming
- `stat particles` - Particle stats
- `stat physics` - Physics metrics
- `stat ai` - AI stats
- `stat anim` - Animation metrics

### Debug & Profiling (10 commands)

Advanced debugging and profiling tools.

| Command | Description |
|---------|-------------|
| `Adastrea: Profile GPU` | Start GPU profiling |
| `Adastrea: Memory Report` | Generate detailed memory report |
| `Adastrea: List Objects` | List all loaded objects |
| `Adastrea: List Classes` | List all loaded classes |
| `Adastrea: Show Debug Overlay` | Show debug information overlay |
| `Adastrea: Show Log Window` | Display log output window |

**Console Commands:**
- `profilegpu` - GPU profiling
- `memreport` - Memory report
- `obj list` - List objects
- `obj classes` - List classes
- `showdebug` - Debug overlay
- `showlog` - Log window

### Rendering (15+ commands)

Control rendering quality and visualization.

| Command | Description |
|---------|-------------|
| `Adastrea: Set Screen Percentage` | Adjust rendering resolution (50-200%) |
| `Adastrea: Toggle VSync` | Enable/disable vertical sync |
| `Adastrea: Visualize Texture` | Visualize texture usage |

**Available in Quick Picker:**
- Screen Percentage: 100%, 75%, 50%
- VSync: Enable/Disable
- Max FPS: 60, 120, Unlimited
- Resolution: 1080p, 1440p
- View Modes: Wireframe, Lit, Unlit
- Visualization tools

**Console Commands:**
- `r.ScreenPercentage [50-200]` - Rendering scale
- `r.VSync [0|1]` - VSync toggle
- `r.MaxFPS [value]` - FPS cap
- `r.SetRes [width]x[height]` - Resolution
- `viewmode [lit|unlit|wireframe]` - View mode
- `r.VisualizeTexture` - Texture visualization

### Gameplay (10 commands)

Control game simulation and capture.

| Command | Description |
|---------|-------------|
| `Adastrea: Pause Game` | Pause/unpause game |
| `Adastrea: Set Game Speed` | Adjust time dilation (0.1-10.0) |
| `Adastrea: Take Screenshot` | Capture screenshot |
| `Adastrea: Take High-Res Screenshot` | Capture high-resolution screenshot |
| `Adastrea: Show Collision` | Visualize collision geometry |
| `Adastrea: Show Bounds` | Visualize object bounds |

**Available in Quick Picker:**
- Game Speed: 0.5x, 1.0x, 2.0x
- Show: Collision, Bounds, Navigation
- Capture: Screenshot, High-Res
- Toggle fullscreen

**Console Commands:**
- `pause` - Pause game
- `slomo [0.1-10.0]` - Time dilation
- `screenshot` - Screenshot
- `highresshot` - High-res screenshot
- `show collision` - Collision viz
- `show bounds` - Bounds viz

### Assets & Content (6 commands)

List and inspect game assets.

| Command | Description |
|---------|-------------|
| `Adastrea: List Textures` | List all loaded textures |
| `Adastrea: List Particle Systems` | List particle systems |
| `Adastrea: List Skeletal Meshes` | List skeletal meshes |
| `Adastrea: List Static Meshes` | List static meshes |

**Available in Quick Picker:**
- Animation sequences
- Materials

**Console Commands:**
- `listtextures` - All textures
- `listparticlesystems` - Particle systems
- `listskeletalmeshes` - Skeletal meshes
- `liststaticmeshes` - Static meshes

### Networking (4 commands)

Network diagnostics and simulation.

| Command | Description |
|---------|-------------|
| `Adastrea: Network Stats` | Display network statistics |

**Available in Quick Picker:**
- Packet lag simulation (100ms)
- Packet loss simulation (5%)
- Network profiling

**Console Commands:**
- `net stat` - Network stats
- `net pktlag [ms]` - Simulate lag
- `net pktloss [percent]` - Simulate packet loss

### Console Management (4 commands)

Explore available commands and variables.

| Command | Description |
|---------|-------------|
| `Adastrea: List Console Commands` | List all console commands |
| `Adastrea: List Console Variables` | List all console variables |
| `Adastrea: Dump Console Commands` | Export console commands |

**Console Commands:**
- `listcmds` - All commands
- `listcvars` - All variables
- `dumpconsolecommands` - Export commands

## Usage Examples

### Example 1: Performance Analysis

1. Open Command Palette (`Ctrl+Shift+P`)
2. Type "Adastrea FPS"
3. Select `Adastrea: Show FPS Stats`
4. Check Unreal Engine viewport for FPS display

### Example 2: Using Quick Picker

1. Open Command Palette
2. Type "Adastrea Quick"
3. Select `Adastrea: Quick Command Picker`
4. Search for "gpu" or "memory"
5. Select command from categorized list

### Example 3: Adjust Rendering Quality

1. Open Command Palette
2. Type "Adastrea Screen"
3. Select `Adastrea: Set Screen Percentage`
4. Enter value (e.g., "75" for 75%)
5. Performance improvement visible immediately

### Example 4: Debug Visualization

1. Use Quick Picker
2. Search "show collision"
3. Execute command
4. See collision geometry in viewport
5. Run again to toggle off

## Command Palette Tips

### Searching
- **By category:** Type "Adastrea UE Stats" to see all stat commands
- **By function:** Type "Adastrea Show" for visualization commands
- **By keyword:** Type "memory", "fps", "render", etc.

### Categories in Command Palette
- `Adastrea Director` - Core Director commands
- `Adastrea UE Stats` - Performance monitoring
- `Adastrea UE Debug` - Debugging tools
- `Adastrea UE Rendering` - Graphics settings
- `Adastrea UE Gameplay` - Game control
- `Adastrea UE Assets` - Asset management
- `Adastrea UE Network` - Networking
- `Adastrea UE Console` - Console utilities

## Keyboard Shortcuts

You can assign keyboard shortcuts to frequently used commands:

1. Open Keyboard Shortcuts (`Ctrl+K Ctrl+S`)
2. Search for "Adastrea"
3. Click the + icon next to any command
4. Press your desired key combination

**Suggested shortcuts:**
- `Ctrl+Alt+F` → Show FPS Stats
- `Ctrl+Alt+U` → Show Unit Stats
- `Ctrl+Alt+P` → Pause Game
- `Ctrl+Alt+Q` → Quick Command Picker

## Custom Commands

For commands not in the preset list, use:

**Command:** `Adastrea: Execute Unreal Command`

Enter any Unreal Engine console command directly.

## Output

All commands output results to the "Adastrea Director" output panel:
- Success/failure status
- Command executed
- Result data (when available)
- Timestamps

## Requirements

- Unreal Engine running with Remote Control enabled
- IPC Server connected
- Valid Remote Control endpoint (localhost:30010)

## Troubleshooting

### Command not working
1. Check Unreal Engine is running
2. Verify Remote Control is enabled (`-RCWebControlEnable`)
3. Test connection: `Adastrea: Check Unreal Connection`

### No output shown
Many commands display results in the Unreal Engine viewport, not the output panel. Check the UE window.

### Command list not showing
Make sure you're connected to the Director IPC server first.

## Complete Command List

**Total: 50+ dedicated commands + 160+ via Quick Picker**

### Dedicated Commands (50)
- 4 Core commands (Check, Execute, Get/Set Property)
- 14 Performance stats
- 6 Debug & profiling
- 3 Rendering
- 6 Gameplay
- 4 Assets
- 1 Networking
- 3 Console
- 1 Quick Command Picker
- 2 Interactive (Screen %, Slomo)
- 6 Property/connection management

### Quick Picker Commands (160+)
- 70+ variations of stat commands
- 40+ rendering settings
- 20+ debug tools
- 15+ gameplay controls
- 10+ asset listings
- 5+ network tools

## Documentation

- **Implementation Guide:** `REMOTE_CONTROL_VSCODE_INTEGRATION.md`
- **Integration Status:** `REMOTE_CONTROL_INTEGRATION_STATUS.md`
- **Quick Reference:** `REMOTE_CONTROL_QUICK_REF.md`

---

**Last Updated:** 2026-01-05
**Version:** 2.0 (Extended Command Set)
