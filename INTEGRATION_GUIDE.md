# Adastrea Director - Integration Guide

**Last Updated:** 2025-11-13  
**Target Audience:** Developers integrating Director into their workflow  
**Based On:** [ADASTREA_DIRECTOR_ANALYSIS.md](ADASTREA_DIRECTOR_ANALYSIS.md)

---

## Overview

This guide walks you through integrating Adastrea Director into your Unreal Engine game development workflow, from initial setup to daily usage. Follow the milestones in order for the smoothest adoption experience.

**Total Time Investment:** 4-6 weeks for full integration  
**Immediate Value:** Available from Day 1 with Phases 1-2

---

## Quick Start (30 Minutes)

For impatient developers who want to see value immediately:

```bash
# 1. Clone and setup (5 minutes)
git clone https://github.com/Mittenzx/Adastrea-Director.git
cd Adastrea-Director
./setup.sh

# 2. Configure API key (2 minutes)
export OPENAI_API_KEY="your-key-here"

# 3. Test Phase 1 - Documentation Q&A (5 minutes)
python main.py
> "What is the main gameplay loop?"

# 4. Test Phase 2 - Planning (10 minutes)
python planning_cli.py --interactive
> "Add a new inventory system to my game"

# 5. Review the plan (8 minutes)
# Examine the generated tasks, dependencies, and code suggestions
```

**Result:** You now understand what Director can do. Continue to Milestone 1 for full setup.

---

## Milestone 1: Foundation Setup (Week 1-2)

**Goal:** Get Director operational with your game project's documentation.

### Tasks

#### 1. Clone and Install (30 minutes)

```bash
# Clone repository
cd ~/projects
git clone https://github.com/Mittenzx/Adastrea-Director.git
cd Adastrea-Director

# Run automated setup
./setup.sh  # Linux/Mac
# or
python install_dependencies.py  # Windows

# Verify installation
python -m pytest tests/ -v
```

**Expected Result:** All tests pass (161 tests for Phase 1-2).

#### 2. Configure API Keys (5 minutes)

Create a `.env` file in the project root:

```bash
# Required for LLM queries
OPENAI_API_KEY=your-openai-api-key-here

# Optional: For ingesting private game repositories
GITHUB_TOKEN=your-github-token-here
```

**Cost Estimate:** $0.05-0.10 per query session (10-20 queries)

#### 3. Ingest Project Documentation (1-2 hours)

**Priority 1: Core Game Systems**
```bash
# Ingest your game's documentation
python ingest.py --docs-dir ~/YourGame/Documentation

# For Adastrea game specifically
python ingest_game_repo.py
```

**Priority 2: Code and Assets**
```bash
# Ingest source code for context
python ingest.py --docs-dir ~/YourGame/Source --pattern "*.h" --pattern "*.cpp"
python ingest.py --docs-dir ~/YourGame/Source --pattern "*.py"

# Ingest data assets and configs
python ingest.py --docs-dir ~/YourGame/Content --pattern "*.yaml" --pattern "*.json"
```

**What to Ingest:**
- ✅ Design documents (GDD, system designs)
- ✅ Technical documentation
- ✅ API references
- ✅ YAML templates and configs
- ✅ README files and guides
- ✅ C++ headers for API understanding
- ❌ Skip: Binary assets, compiled code, large data files

**Expected Result:** 
- 200+ documents ingested
- ~5-10 seconds ingestion time
- ~500MB RAM for full knowledge base

#### 4. Test Core Workflows (30 minutes)

**Test 1: Documentation Q&A**
```python
python main.py
```
```
> How do I create a new character ability?
> What's the proper way to add a faction?
> Explain the save system architecture
```

**Test 2: Feature Planning**
```bash
python planning_cli.py "Add a reputation system between factions"
```

**Test 3: Bug Investigation**
```python
python main.py
```
```
> Why might my character stats fail to persist across save/load?
```

**Expected Results:**
- Phase 1: Answers reference specific documentation with context
- Phase 2: Plans include 8-12 tasks with dependencies and code snippets
- Response time: <2 seconds for Phase 1, ~20-30 seconds for Phase 2

### Deliverables

- ✅ Working Director installation
- ✅ Indexed game knowledge base (200+ documents)
- ✅ Verified Q&A and planning capabilities
- ✅ Setup documentation for team members

### Success Criteria

- [ ] All tests passing
- [ ] <2 second query response time
- [ ] Accurate answers to project-specific questions
- [ ] Successful task decomposition for sample goals
- [ ] Team members can set up in <1 hour following your docs

---

## Milestone 2: Daily Workflow Integration (Week 3-4)

**Goal:** Make Director a natural part of your development process.

### Tasks

#### 1. Create Quick-Reference Materials (2 hours)

**Cheat Sheet Example:**
```markdown
# Adastrea Director Quick Reference

## Common Commands

# Documentation Q&A
python main.py

# Plan a new feature
python planning_cli.py "your goal here"

# Interactive planning
python planning_cli.py --interactive

# Export plan to file
python planning_cli.py "goal" --output plan.md

## Best Practices

- Be specific in your questions
- Reference system names from your docs
- Review generated plans before implementation
- Update documentation regularly for accurate answers
```

#### 2. Set Up IDE Integration (1-2 hours)

**VS Code Integration (Recommended):**
```json
// .vscode/tasks.json
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "Ask Director",
      "type": "shell",
      "command": "python",
      "args": ["${workspaceFolder}/../Adastrea-Director/main.py"],
      "problemMatcher": [],
      "group": "none"
    },
    {
      "label": "Plan Feature",
      "type": "shell",
      "command": "python",
      "args": [
        "${workspaceFolder}/../Adastrea-Director/planning_cli.py",
        "${input:goalDescription}"
      ],
      "problemMatcher": []
    }
  ],
  "inputs": [
    {
      "id": "goalDescription",
      "type": "promptString",
      "description": "Describe the feature or goal"
    }
  ]
}
```

**Keyboard Shortcuts:**
```bash
# Add to your shell profile (.bashrc, .zshrc)
alias director='cd ~/projects/Adastrea-Director && python main.py'
alias plan='cd ~/projects/Adastrea-Director && python planning_cli.py'
```

#### 3. Integrate with Team Workflow (2-3 hours)

**Morning Standup Integration:**
- Review Director-generated plans for the day
- Ask Director about any blockers or questions
- Plan sprint tasks with Director assistance

**Feature Development Process:**
```
1. Write feature description
2. Run: python planning_cli.py "feature description" --output feature-plan.md
3. Review plan with team
4. Refine tasks as needed
5. Implement following the plan
6. Update documentation for future Director queries
```

**Code Review Process:**
- Use Director to explain unfamiliar code sections
- Verify implementation against original plan
- Ask Director about best practices

#### 4. Train Team (2 hours)

**Training Session Agenda:**
1. Demo Phase 1 Q&A (15 minutes)
2. Demo Phase 2 Planning (15 minutes)
3. Hands-on practice (30 minutes)
4. Common use cases (15 minutes)
5. Best practices and tips (15 minutes)
6. Q&A (30 minutes)

**Training Materials:**
- Quick-start guide
- Cheat sheet
- Example queries and plans
- Video walkthrough (optional)

#### 5. Collect Feedback (Ongoing)

**Feedback System:**
```markdown
# Director Feedback Log

## Date: YYYY-MM-DD
## Feature: [Phase 1 Q&A / Phase 2 Planning]
## User: [Name]

### What Worked Well
- ...

### What Needs Improvement
- ...

### Feature Requests
- ...

### Overall Rating: [1-5 stars]
```

**Weekly Review:**
- Compile feedback
- Identify common issues
- Prioritize improvements
- Update documentation

### Deliverables

- ✅ Quick-reference cheat sheet
- ✅ IDE integration (tasks, shortcuts)
- ✅ Team training materials
- ✅ Feedback collection system
- ✅ Updated workflow documentation

### Success Criteria

- [ ] 50%+ team adoption within 2 weeks
- [ ] Positive feedback (>70% satisfaction)
- [ ] Daily active usage by at least 2 team members
- [ ] <5 minute average time to get answers
- [ ] Plans used in at least 50% of new features

---

## Milestone 3: Enhanced Capabilities (Week 5-6)

**Goal:** Add project-specific enhancements and validation.

### Priority Enhancement: YAML Validation

**Why:** Ensures Director generates valid YAML matching your schemas.

**Implementation Time:** 1-2 weeks

**Steps:**

1. **Create Schema Validator Integration** (if you have one)
```python
# In your project, create schema_validator.py
def validate_yaml(yaml_content: str, schema_type: str) -> ValidationResult:
    """Validate YAML against your game's schema."""
    # Your validation logic here
    pass
```

2. **Integrate with Director's Code Generation Agent**
```python
# Add to code_generation_agent.py
from your_game.schema_validator import validate_yaml

def generate_yaml_template(self, task: Task) -> str:
    template = self._create_template(task)
    
    # Validate before returning
    validation = validate_yaml(template, task.schema_type)
    if not validation.is_valid:
        # Attempt to fix or raise error
        template = self._fix_yaml_errors(template, validation.errors)
    
    return template
```

3. **Test Validation**
```bash
python planning_cli.py "Create a new spaceship data asset"
# Verify generated YAML is valid for your schema
```

**Success Criteria:**
- [ ] 100% valid YAML generation
- [ ] Clear error messages for violations
- [ ] Automatic correction of common mistakes
- [ ] No manual validation needed

### Optional Enhancement: Cost Tracking

**Implementation:**
```python
# Create cost_tracker.py
class CostTracker:
    def __init__(self):
        self.session_costs = {}
    
    def track_call(self, agent_id: str, tokens: int):
        cost = self._calculate_cost(tokens)
        self.session_costs[agent_id] = self.session_costs.get(agent_id, 0) + cost
    
    def get_daily_cost(self) -> float:
        return sum(self.session_costs.values())
    
    def _calculate_cost(self, tokens: int) -> float:
        # GPT-4 pricing: ~$0.03/1K input tokens, ~$0.06/1K output tokens
        return tokens * 0.00003  # Simplified
```

**Integration:**
```python
# Add to main.py and planning_cli.py
cost_tracker = CostTracker()

# After each LLM call
cost_tracker.track_call("query_agent", response.total_tokens)

# Display at session end
print(f"Session cost: ${cost_tracker.get_daily_cost():.2f}")
```

### Deliverables

- ✅ YAML validation integrated
- ✅ Cost tracking implemented (optional)
- ✅ Enhanced Code Generation Agent
- ✅ Test suite for new features

### Success Criteria

- [ ] YAML validation working for all template types
- [ ] Cost tracking shows accurate estimates
- [ ] No regression in existing functionality
- [ ] Performance impact <5%

---

## Milestone 4: Phase 3 Preparation (Week 7-10)

**Goal:** Prepare infrastructure for autonomous agents.

**Note:** This milestone prepares for Phase 3 but doesn't implement it fully. Full Phase 3 is an 8-12 week effort.

### Tasks

#### 1. Enable Unreal Remote Control Plugin (1 hour)

In your Unreal Engine project:

1. **Enable Plugin**
   - Edit → Plugins → Search "Remote Control"
   - Enable "Remote Control API"
   - Restart editor

2. **Configure Remote Control**
   - Edit → Project Settings → Remote Control
   - Enable "Remote Control Web Interface"
   - Set port (default: 7001)
   - Enable "Remote Control Web Server"

3. **Expose Properties/Functions**
```cpp
// In your game classes
UPROPERTY(BlueprintReadWrite, Meta = (ExposeOnSpawn))
float PlayerHealth;

UFUNCTION(BlueprintCallable, Meta = (RemoteControl))
void TakeDamage(float Amount);
```

4. **Test Connection**
```bash
curl http://localhost:7001/remote/info
```

**Expected Result:** JSON response with Remote Control API info.

#### 2. Set Up Test Environments (2-3 hours)

**Create Test Level:**
- Minimal level for automated testing
- Test actors for each major system
- Performance measurement points
- Automated test sequences

**Performance Benchmarks:**
```cpp
// UE4/5 Console commands for benchmarking
stat fps
stat unit
stat gpu
stat memory
```

Document baseline performance:
- Target FPS: 60+
- Memory usage: <4GB
- Frame time: <16.67ms

#### 3. Design Event Bus Architecture (4-6 hours)

**Event Types:**
```python
class EventType(Enum):
    PERFORMANCE_ALERT = "performance_alert"
    BUG_DETECTED = "bug_detected"
    CODE_QUALITY_ISSUE = "code_quality_issue"
    TEST_COMPLETED = "test_completed"
    METRICS_COLLECTED = "metrics_collected"
```

**Event Bus Implementation:**
```python
# Create event_bus.py
class EventBus:
    def __init__(self):
        self._subscribers = defaultdict(list)
    
    def subscribe(self, event_type: EventType, handler: Callable):
        self._subscribers[event_type].append(handler)
    
    def publish(self, event: Event):
        for handler in self._subscribers[event.type]:
            handler(event)
    
    def unsubscribe(self, event_type: EventType, handler: Callable):
        self._subscribers[event_type].remove(handler)
```

**Example Usage:**
```python
# Performance Agent subscribes to metrics
event_bus.subscribe(
    EventType.METRICS_COLLECTED,
    performance_agent.analyze_metrics
)

# Bug Detection Agent publishes findings
event_bus.publish(Event(
    type=EventType.BUG_DETECTED,
    data={"bug": bug_report, "severity": "high"}
))
```

#### 4. Implement Shared Context (2-3 hours)

```python
# Create shared_context.py
class SharedContext:
    def __init__(self):
        self._context = {}
        self._lock = threading.Lock()
    
    def get_project_info(self) -> ProjectInfo:
        return self._context.get("project_info")
    
    def get_recent_changes(self) -> List[Change]:
        return self._context.get("recent_changes", [])
    
    def update_context(self, key: str, value: Any):
        with self._lock:
            self._context[key] = value
    
    def get_conversation_history(self) -> List[Message]:
        return self._context.get("conversation_history", [])
```

#### 5. Documentation and Planning (2-3 hours)

Create architecture documentation:
- Event bus design and usage
- Shared context schema
- Agent communication protocol
- Remote Control API integration plan

### Deliverables

- ✅ Remote Control API enabled and tested
- ✅ Test environments configured
- ✅ Performance baselines documented
- ✅ Event bus implemented
- ✅ Shared context system implemented
- ✅ Architecture documentation complete

### Success Criteria

- [ ] Remote Control API responding to HTTP requests
- [ ] Basic commands working (stat fps, etc.)
- [ ] Event bus tested with mock events
- [ ] Shared context thread-safe and tested
- [ ] Architecture reviewed by team

---

## Ongoing Maintenance

### Weekly Tasks (30 minutes)

1. **Update Knowledge Base**
   - Re-ingest changed documentation
   - Verify query accuracy
   - Remove outdated documents

```bash
# Check for changed docs
git -C ~/YourGame diff --name-only HEAD@{7.days.ago} -- Documentation/

# Re-ingest changed files
python ingest.py --docs-dir ~/YourGame/Documentation --incremental
```

2. **Review Feedback**
   - Collect team feedback
   - Identify common issues
   - Prioritize improvements

3. **Monitor Costs**
   - Review API usage
   - Check monthly spending
   - Optimize expensive queries

### Monthly Tasks (2 hours)

1. **Update Director**
```bash
cd ~/projects/Adastrea-Director
git pull origin main
pip install -r requirements.txt --upgrade
python -m pytest tests/
```

2. **Review Integration**
   - Measure team adoption
   - Analyze usage patterns
   - Update workflows as needed

3. **Plan Improvements**
   - Review [IMPROVEMENTS.md](IMPROVEMENTS.md)
   - Prioritize next enhancements
   - Schedule implementation

---

## Troubleshooting

### Common Issues

**Issue: Queries return irrelevant results**
- **Cause:** Outdated or incomplete knowledge base
- **Fix:** Re-ingest documentation, ensure all docs included

**Issue: Plans are too generic**
- **Cause:** Insufficient project context
- **Fix:** Ingest more code and documentation for context

**Issue: YAML validation fails**
- **Cause:** Schema mismatch or outdated schemas
- **Fix:** Update schema files, verify integration

**Issue: High API costs**
- **Cause:** Inefficient queries or large context windows
- **Fix:** Implement cost tracking, optimize query patterns

**Issue: Remote Control not responding**
- **Cause:** Plugin not enabled or port conflict
- **Fix:** Verify plugin enabled, check port availability

For more issues, see [TROUBLESHOOTING.md](docs/guides/TROUBLESHOOTING.md)

---

## Success Metrics

Track these metrics to measure integration success:

| Metric | Week 2 Target | Week 6 Target | Month 3 Target |
|--------|---------------|---------------|----------------|
| Team Adoption | 30% | 50% | 70%+ |
| Daily Active Users | 1-2 | 2-3 | 3-4 |
| Questions per Week | 10-20 | 30-50 | 50-100 |
| Plans Generated per Week | 2-5 | 5-10 | 10-20 |
| User Satisfaction | 60% | 70% | 80%+ |
| Time Saved (hours/week) | 5-10 | 20-30 | 40-60 |

---

## ROI Tracking

### Cost Tracking

**Monthly Costs:**
- OpenAI API (Phase 1-2): $50-100
- Maintenance time: $500-1,000 (2-4 hours @ $250/hr)
- **Total:** $550-1,100/month

**Time Savings:**
- Documentation lookup: 15 hours/month @ $50/hr = $750
- Feature planning: 20 hours/month @ $50/hr = $1,000
- Bug investigation: 20 hours/month @ $50/hr = $1,000
- **Total:** 55+ hours/month = $2,750+/month

**Net Benefit:** $1,650-2,200/month or ~$20-26k/year

### Payback Period

**Initial Investment:** ~$7,000 (setup + integration)  
**Monthly Net Benefit:** ~$2,000  
**Payback Period:** ~3.5 months (lower than 6-month analysis estimate)

---

## Next Steps

After completing all milestones:

1. **Evaluate Phase 3 Readiness**
   - Review [PHASE3_GUIDE.md](PHASE3_GUIDE.md)
   - Assess team readiness for autonomous agents
   - Plan Phase 3 kickoff

2. **Continuous Improvement**
   - Implement high-priority improvements from [IMPROVEMENTS.md](IMPROVEMENTS.md)
   - Optimize based on usage patterns
   - Expand knowledge base

3. **Share Success**
   - Document learnings
   - Share with community
   - Contribute improvements back to Director

---

## Resources

- **Analysis Report:** [ADASTREA_DIRECTOR_ANALYSIS.md](ADASTREA_DIRECTOR_ANALYSIS.md)
- **Improvements:** [IMPROVEMENTS.md](IMPROVEMENTS.md)
- **Project Roadmap:** [ROADMAP.md](ROADMAP.md)
- **Phase 3 Guide:** [PHASE3_GUIDE.md](PHASE3_GUIDE.md)
- **Troubleshooting:** [docs/guides/TROUBLESHOOTING.md](docs/guides/TROUBLESHOOTING.md)

---

## Support

- **Issues:** [GitHub Issues](https://github.com/Mittenzx/Adastrea-Director/issues)
- **Discussions:** [GitHub Discussions](https://github.com/Mittenzx/Adastrea-Director/discussions)
- **Documentation:** [docs/INDEX.md](docs/INDEX.md)

---

**Status:** Living document - update as you learn and improve your integration.

**Feedback:** Please share your integration experience to help improve this guide!
