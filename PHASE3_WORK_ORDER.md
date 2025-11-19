# Phase 3: Autonomous Agents - Detailed Work Order

**Document Version:** 1.0  
**Created:** November 19, 2025  
**Status:** Active Work Plan  
**Estimated Timeline:** 6-8 weeks remaining

---

## Executive Summary

Phase 3 core implementation is **COMPLETE**. This document provides a precise, step-by-step work order for completing the remaining critical enhancements and integrations that will make Phase 3 production-ready for Unreal Engine game development.

### Completion Status

**✅ COMPLETED** (November 2025):
- All 3 autonomous agents fully implemented
- Event Bus and Shared State infrastructure
- Agent Orchestrator CLI and Dashboard
- 120 comprehensive tests (100% passing)
- Complete documentation (PHASE3_GUIDE.md)
- Demo scripts and examples

**⏳ REMAINING** (This Work Order):
- Unreal Engine Remote Control integration (Weeks 1-2)
- Blueprint support system (Weeks 3-5)
- YAML template validation (Week 6)
- GitHub Issues integration (Week 7)
- Cost tracking implementation (Week 8)
- Final integration and testing (Weeks 9-10)

---

## Work Breakdown by Week

### Week 1-2: Unreal Engine Remote Control Integration

**Goal:** Establish bidirectional communication between Adastrea Director and Unreal Engine.

**Priority:** CRITICAL - Foundation for all agent UE integration

#### Step 1.1: Remote Control API Research & Setup (Days 1-2)

**Tasks:**
1. **Install Unreal Engine Remote Control Plugin**
   - Enable WebControl plugin in Unreal Editor
   - Configure HTTP/WebSocket endpoints
   - Document connection settings (default: http://localhost:30010)
   - Test basic connectivity with curl/Postman

2. **Review Unreal MCP Server**
   - Clone [ChiR24/Unreal_mcp](https://github.com/ChiR24/Unreal_mcp)
   - Review 13 available tools
   - Identify which tools agents need
   - Document tool capabilities and limitations

3. **Create Remote Control Configuration**
   - Add UE connection settings to config/config.yaml
   - Create remote_control_config.py for managing settings
   - Add environment variables for UE host/port
   - Implement connection health check

**Deliverables:**
- `config/remote_control_config.py` - Configuration management
- `docs/UNREAL_REMOTE_CONTROL_SETUP.md` - Setup guide
- Connection test script

**Success Criteria:**
- [ ] Successfully connect to UE Remote Control API
- [ ] Execute basic console commands (stat fps, stat memory)
- [ ] Retrieve actor list from current level
- [ ] Documentation complete with screenshots

#### Step 1.2: Python HTTP Client Implementation (Days 3-4)

**Tasks:**
1. **Create HTTP Client Class**
   ```python
   # remote_control/http_client.py
   class UnrealHTTPClient:
       def __init__(self, host: str, port: int) -> None
       def connect(self) -> bool
       def execute_console_command(self, command: str) -> CommandResult
       def get_property(self, object_path: str, property_name: str) -> Any
       def set_property(self, object_path: str, property_name: str, value: Any) -> bool
       def call_function(self, object_path: str, function_name: str, parameters: Dict) -> Any
       def get_actors_in_level(self) -> List[ActorInfo]
       def health_check(self) -> HealthStatus
   ```

2. **Implement Error Handling**
   - Connection timeouts (5 second default)
   - Retry logic with exponential backoff
   - Graceful degradation when UE not running
   - Comprehensive error logging

3. **Add Response Parsing**
   - Parse JSON responses
   - Convert to Python dataclasses
   - Handle error responses
   - Validate data types

**Deliverables:**
- `remote_control/http_client.py` - HTTP client implementation
- `remote_control/models.py` - Response data models
- Unit tests for HTTP client (20+ tests)

**Success Criteria:**
- [ ] Successfully execute all common console commands
- [ ] Retrieve and set actor properties
- [ ] Handle connection errors gracefully
- [ ] 90%+ test coverage

#### Step 1.3: WebSocket Client for Real-Time Events (Days 5-6)

**Tasks:**
1. **Implement WebSocket Client**
   ```python
   # remote_control/websocket_client.py
   class UnrealWebSocketClient:
       def __init__(self, host: str, port: int) -> None
       async def connect(self) -> bool
       async def subscribe_to_property(self, object_path: str, property_name: str)
       async def on_property_changed(self, callback: Callable)
       async def disconnect(self)
   ```

2. **Real-Time Event Handling**
   - Property change notifications
   - Actor spawn/destroy events
   - Level load events
   - PIE (Play In Editor) state changes

3. **Integration with Event Bus**
   - Forward UE events to Phase 3 Event Bus
   - Map UE events to EventType enum
   - Add new event types as needed

**Deliverables:**
- `remote_control/websocket_client.py` - WebSocket implementation
- Integration with Phase 3 Event Bus
- Example real-time monitoring script

**Success Criteria:**
- [ ] Receive real-time property updates
- [ ] Detect PIE start/stop events
- [ ] Forward events to Event Bus correctly
- [ ] Async operations work correctly

#### Step 1.4: Integration with Phase 3 Agents (Days 7-10)

**Tasks:**
1. **Update Performance Profiling Agent**
   ```python
   # agents/phase3/performance_profiling_agent.py
   
   def collect_metrics_from_ue(self) -> PerformanceMetrics:
       """
       Collect real performance metrics from Unreal Engine via Remote Control API.
       
       Returns:
           PerformanceMetrics: An object containing FPS, memory usage, and GPU statistics.
       
       Raises:
           ConnectionError: If Unreal Engine is not connected or metrics cannot be retrieved.
       """
       # Execute: stat fps, stat memory, stat gpu
       # Parse console output
       # Return PerformanceMetrics
   
   def start_pie_profiling(self) -> None:
       """Start profiling during PIE session"""
       # Detect PIE start event
       # Begin metric collection loop
       # Analyze performance in real-time
   ```

2. **Update Bug Detection Agent**
   ```python
   # agents/phase3/bug_detection_agent.py
   
   def monitor_ue_logs(self, log_file_path: str) -> None:
       """Monitor UE log file in real-time"""
       # Tail log file
       # Detect errors/warnings/crashes
       # Create anomaly reports
   
   def automated_playtest(self, test_sequence: str) -> TestResults:
       """Run automated playtest via Sequencer"""
       # Start PIE
       # Execute test sequence
       # Monitor for errors
       # Generate report
   ```

3. **Update Code Quality Agent**
   ```python
   # agents/phase3/code_quality_agent.py
   
   def analyze_blueprint(self, blueprint_path: str) -> QualityReport:
       """
       Analyze Blueprint complexity and detect quality issues in a given Unreal Engine Blueprint (.uasset) file.
       
       Args:
           blueprint_path (str): Path to the Blueprint .uasset file to be analyzed.
       
       Returns:
           QualityReport: An object containing complexity metrics and detected anti-patterns.
       
       Raises:
           NotImplementedError: This method is a placeholder and will be implemented in Weeks 3-5.
       
       Expected Behavior:
           - Parse the Blueprint file and extract relevant metrics (e.g., node count, graph complexity).
           - Identify common anti-patterns and code quality issues.
           - Return a comprehensive QualityReport summarizing findings.
       """
       # To be implemented with Blueprint support
       pass
   ```

4. **Create Unified Remote Control Manager**
   ```python
   # remote_control/manager.py
   class RemoteControlManager:
       def __init__(self, event_bus: EventBus) -> None
       def connect_to_ue(self) -> bool
       def disconnect(self) -> None
       def is_connected(self) -> bool
       def get_http_client(self) -> UnrealHTTPClient
       def get_websocket_client(self) -> UnrealWebSocketClient
   ```

**Deliverables:**
- Updated agent implementations with UE integration
- `remote_control/manager.py` - Unified manager
- Integration tests (30+ tests)
- Updated PHASE3_GUIDE.md with UE usage examples

**Success Criteria:**
- [ ] Performance agent collects real UE metrics
- [ ] Bug agent monitors UE logs in real-time
- [ ] Agents gracefully handle UE not running
- [ ] All integration tests pass

**Week 1-2 Completion Checklist:**
- [ ] Remote Control API connection working
- [ ] HTTP client fully implemented and tested
- [ ] WebSocket client operational
- [ ] All 3 agents integrated with UE
- [ ] Documentation updated
- [ ] 50+ new tests passing

---

### Week 3-5: Blueprint Support System

**Goal:** Enable analysis of Unreal Engine Blueprint graphs for complexity, patterns, and quality issues.

**Priority:** HIGH - Blueprints are core to UE development

#### Step 2.1: Blueprint Parser Research & Design (Days 1-3)

**Tasks:**
1. **Research Blueprint File Format**
   - Analyze .uasset file structure
   - Identify node graph representation
   - Research existing parsing libraries
   - Document Blueprint metadata format

2. **Design Blueprint Data Model**
   ```python
   # agents/blueprint/models.py
   
   @dataclass
   class BlueprintNode:
       node_id: str
       node_type: str  # Function, Event, Branch, etc.
       position: Tuple[int, int]
       connections: List[str]  # Connected node IDs
       properties: Dict[str, Any]
   
   @dataclass
   class BlueprintGraph:
       blueprint_path: str
       graph_name: str
       nodes: List[BlueprintNode]
       complexity: int
       entry_points: List[str]
       
       def calculate_cyclomatic_complexity(self) -> int
       def find_long_execution_paths(self) -> List[Path]
       def detect_duplicate_logic(self) -> List[DuplicatePattern]
   ```

3. **Identify Analysis Metrics**
   - Node count per graph
   - Cyclomatic complexity
   - Execution path length
   - Variable count
   - Function call depth
   - Duplicate logic patterns

**Deliverables:**
- `agents/blueprint/models.py` - Data models
- `docs/BLUEPRINT_FORMAT.md` - Format documentation
- Blueprint analysis design document

**Success Criteria:**
- [ ] Blueprint file format understood
- [ ] Data model designed
- [ ] Analysis metrics defined
- [ ] Approach validated with sample Blueprint

#### Step 2.2: Blueprint Parser Implementation (Days 4-8)

**Tasks:**
1. **Implement Blueprint File Parser**
   ```python
   # agents/blueprint/parser.py
   
   class BlueprintParser:
       def parse_blueprint_file(self, file_path: str) -> BlueprintGraph
       def extract_node_graph(self, asset_data: bytes) -> List[BlueprintNode]
       def identify_connections(self, nodes: List[BlueprintNode]) -> None
       def extract_metadata(self, asset_data: bytes) -> Dict[str, Any]
   ```

2. **Use Unreal Python API or MCP Tools**
   - Option A: Use UE Python API to export Blueprint data
   - Option B: Use Unreal MCP `manage_blueprint` tool
   - Option C: Parse .uasset files directly (complex)
   - **Recommendation:** Use UE Python API for reliability

3. **Create Blueprint Export Script**
   ```python
   # In Unreal Engine (Python):
   # scripts/export_blueprint_data.py
   
   import unreal
   
   def export_blueprint_to_json(blueprint_path: str) -> str:
       """
       Export Blueprint graph to JSON for analysis.
       
       Args:
           blueprint_path (str): Path to the Blueprint asset in Unreal Engine.
       
       Returns:
           str: A JSON string containing the node graph structure, with the following format:
               {
                   "nodes": [
                       {
                           "id": <node_id>,
                           "type": <node_type>,
                           "properties": { ... }
                       },
                       ...
                   ],
                   "connections": [
                       {
                           "from": <source_node_id>,
                           "to": <target_node_id>,
                           "type": <connection_type>
                       },
                       ...
                   ],
                   "metadata": { ... }
               }
           If an error occurs, returns an empty string ("").
       """
       # Load Blueprint asset
       # Extract node graph
       # Serialize to JSON
       # Return JSON string
   ```

**Deliverables:**
- `agents/blueprint/parser.py` - Parser implementation
- `scripts/export_blueprint_data.py` - UE export script
- Unit tests for parser (25+ tests)

**Success Criteria:**
- [ ] Successfully parse sample Blueprints
- [ ] Extract all nodes and connections
- [ ] Calculate correct complexity metrics
- [ ] Handle malformed Blueprints gracefully

#### Step 2.3: Blueprint Analyzer Implementation (Days 9-12)

**Tasks:**
1. **Create Blueprint Analyzer**
   ```python
   # agents/blueprint/analyzer.py
   
   class BlueprintAnalyzer:
       def analyze_complexity(self, graph: BlueprintGraph) -> ComplexityReport
       def detect_antipatterns(self, graph: BlueprintGraph) -> List[AntiPattern]
       def suggest_refactoring(self, graph: BlueprintGraph) -> List[Refactoring]
       def calculate_quality_score(self, graph: BlueprintGraph) -> float
   ```

2. **Implement Anti-Pattern Detection**
   - Long execution paths (>30 nodes)
   - Deep nesting (>5 levels)
   - Unused variables
   - Missing null checks
   - Tight coupling
   - God object Blueprints

3. **Generate Refactoring Suggestions**
   - Extract to function
   - Reduce complexity
   - Add null checks
   - Split large graphs
   - Remove duplicate logic

**Deliverables:**
- `agents/blueprint/analyzer.py` - Analyzer implementation
- Anti-pattern detection rules
- Refactoring suggestion templates
- Unit tests (30+ tests)

**Success Criteria:**
- [ ] Detect >80% of known anti-patterns
- [ ] Generate actionable refactoring suggestions
- [ ] Quality scores align with manual assessment
- [ ] All tests passing

#### Step 2.4: Integration with Code Quality Agent (Days 13-15)

**Tasks:**
1. **Update Code Quality Agent**
   ```python
   # agents/phase3/code_quality_agent.py
   
   def analyze_blueprint_quality(self, blueprint_path: str) -> QualityReport:
       """Analyze Blueprint code quality"""
       parser = BlueprintParser()
       analyzer = BlueprintAnalyzer()
       
       graph = parser.parse_blueprint_file(blueprint_path)
       complexity = analyzer.analyze_complexity(graph)
       antipatterns = analyzer.detect_antipatterns(graph)
       refactorings = analyzer.suggest_refactoring(graph)
       
       return QualityReport(
           file_path=blueprint_path,
           file_type='blueprint',
           complexity_score=complexity.score,
           code_smells=self._convert_antipatterns(antipatterns),
           refactorings=refactorings,
           overall_score=analyzer.calculate_quality_score(graph)
       )
   ```

2. **Add Blueprint Support to CLI**
   - Add `--blueprint` flag to quality analysis commands
   - Display Blueprint-specific metrics
   - Export Blueprint reports

3. **Update Documentation**
   - Add Blueprint analysis section to PHASE3_GUIDE.md
   - Create Blueprint examples
   - Document anti-patterns with visuals

**Deliverables:**
- Updated Code Quality Agent with Blueprint support
- CLI updates for Blueprint analysis
- Integration tests (20+ tests)
- Documentation updates

**Success Criteria:**
- [ ] Code Quality Agent analyzes Blueprints correctly
- [ ] CLI commands work for Blueprints
- [ ] Blueprint reports are clear and actionable
- [ ] Documentation complete with examples

**Week 3-5 Completion Checklist:**
- [ ] Blueprint parser implemented and tested
- [ ] Blueprint analyzer detects anti-patterns
- [ ] Integration with Code Quality Agent complete
- [ ] 75+ new tests passing
- [ ] Documentation updated with Blueprint examples

---

### Week 6: YAML Template Validation

**Goal:** Ensure all generated YAML templates are valid against project schemas.

**Priority:** HIGH - Quick win, high impact

#### Step 3.1: YAML Schema Integration (Days 1-2)

**Tasks:**
1. **Identify YAML Schema Libraries**
   - Research: `jsonschema`, `yamale`, `pykwalify`
   - Choose best fit (recommendation: `jsonschema` with YAML)
   - Install and configure

2. **Collect Project YAML Schemas**
   - Identify all YAML types in project (configs, data tables, etc.)
   - Create or import JSON schemas for each type
   - Store in `schemas/` directory

3. **Create Schema Manager**
   ```python
   # validation/schema_manager.py
   
   class SchemaManager:
       def __init__(self, schema_dir: str) -> None
       def load_schemas(self) -> None
       def get_schema(self, schema_type: str) -> Dict
       def validate_yaml(self, yaml_content: str, schema_type: str) -> ValidationResult
       def auto_detect_schema_type(self, yaml_content: str) -> Optional[str]
   ```

**Deliverables:**
- `validation/schema_manager.py` - Schema management
- `schemas/` directory with project schemas
- Schema documentation

**Success Criteria:**
- [ ] All project YAML types have schemas
- [ ] Schema manager loads schemas correctly
- [ ] Can validate YAML against schemas

#### Step 3.2: Validator Implementation (Days 3-4)

**Tasks:**
1. **Create YAML Validator**
   ```python
   # validation/yaml_validator.py
   
   class YAMLValidator:
       def __init__(self, schema_manager: SchemaManager) -> None
       
       def validate(self, yaml_content: str, schema_type: str) -> ValidationResult:
           """
           Validate YAML against schema.
           
           Note: This method accepts unparsed YAML content as a string. If YAML parsing fails,
           the validation result will indicate a parsing error separate from schema validation errors.
           
           Args:
               yaml_content: Unparsed YAML content as a string
               schema_type: Type of schema to validate against
           
           Returns:
               ValidationResult containing both parsing and schema validation results
           """
           # Parse YAML
           # Load schema
           # Validate
           # Return detailed results
       
       def suggest_fixes(self, validation_result: ValidationResult) -> List[Fix]:
           """Suggest fixes for validation errors"""
           # Analyze errors
           # Generate fix suggestions
           # Return actionable fixes
       
       def auto_fix(self, yaml_content: str, validation_result: ValidationResult) -> str:
           """Automatically fix common issues"""
           # Apply simple fixes
           # Re-validate
           # Return fixed YAML
   ```

2. **Implement Fix Suggestions**
   - Missing required fields
   - Type mismatches
   - Invalid enum values
   - Format errors

**Deliverables:**
- `validation/yaml_validator.py` - Validator implementation
- Fix suggestion engine
- Unit tests (25+ tests)

**Success Criteria:**
- [ ] Validator detects all schema violations
- [ ] Generates clear, actionable error messages
- [ ] Auto-fix works for common issues
- [ ] All tests passing

#### Step 3.3: Integration with Code Generation Agent (Days 5-7)

**Tasks:**
1. **Update Code Generation Agent**
   ```python
   # agents/code_generation_agent.py
   
   def generate_yaml_template(self, task: Task) -> str:
       """
       Generate YAML with automatic validation.
       
       Args:
           task: Task containing YAML type and generation parameters.
       
       Returns:
           Valid YAML string. If validation fails after auto-fix, returns YAML with embedded error comments.
       
       Validation:
           - The generated YAML is validated against the schema.
           - If validation fails, an auto-fix is attempted.
           - If validation still fails after auto-fix, error messages are embedded as comments in the returned YAML.
       
       Exceptions:
           - This method does not raise exceptions; it always returns a YAML string, with errors embedded if necessary.
       """
       # Generate YAML using LLM
       yaml_content = self._generate_yaml_llm(task)
       
       # Validate
       validator = YAMLValidator(self.schema_manager)
       result = validator.validate(yaml_content, task.yaml_type)
       
       # Auto-fix if needed
       if not result.is_valid:
           yaml_content = validator.auto_fix(yaml_content, result)
           result = validator.validate(yaml_content, task.yaml_type)
       
       # If still invalid, include errors in response
       if not result.is_valid:
           self._include_validation_errors(result)
       
       return yaml_content
   ```

2. **Add Validation to Planning CLI**
   - Validate YAML before displaying to user
   - Show validation status in output
   - Provide fix suggestions

3. **Create Validation Report**
   - Validation status (✓ Valid / ✗ Invalid)
   - Error details with line numbers
   - Fix suggestions
   - Auto-fix options

**Deliverables:**
- Updated Code Generation Agent
- CLI validation integration
- Validation reports
- Integration tests (15+ tests)

**Success Criteria:**
- [ ] 100% of generated YAML is valid
- [ ] Users notified of validation issues immediately
- [ ] Fix suggestions are helpful
- [ ] Auto-fix rate >80% for common errors

**Week 6 Completion Checklist:**
- [ ] YAML validation system operational
- [ ] 100% valid YAML generation
- [ ] Integration with Code Generation Agent complete
- [ ] 40+ new tests passing
- [ ] Documentation updated

---

### Week 7: GitHub Issues Integration

**Goal:** Automatically create GitHub Issues from agent alerts.

**Priority:** MEDIUM-HIGH - Streamlines bug tracking workflow

#### Step 4.1: GitHub API Integration (Days 1-3)

**Tasks:**
1. **Setup GitHub API Client**
   ```python
   # integrations/github_client.py
   
   class GitHubClient:
       def __init__(self, token: str, repo: str) -> None
       
       def create_issue(self, issue: IssueData) -> int:
           """Create a new GitHub Issue"""
           # Format issue body
           # Apply labels
           # Set assignees
           # Create issue via API
           # Return issue number (int)
       
       def get_issue_url(self, issue_number: int) -> str
       def add_comment(self, issue_number: int, comment: str) -> None
       def attach_file(self, issue_number: int, file_path: str) -> None
       def apply_labels(self, issue_number: int, labels: List[str]) -> None
       def close_issue(self, issue_number: int) -> None
   ```

2. **Configure GitHub Access**
   - Add GITHUB_TOKEN to .env
   - Add GITHUB_REPO to config
   - Document token permissions needed
   - Test API access

3. **Create Issue Templates**
   ```python
   # integrations/issue_templates.py
   
   class IssueTemplate:
       @staticmethod
       def bug_report(bug: BugReport) -> str:
           """Format bug report as GitHub Issue"""
       
       @staticmethod
       def performance_alert(alert: PerformanceAnalysis) -> str:
           """Format performance alert as GitHub Issue"""
       
       @staticmethod
       def code_quality_issue(report: QualityReport) -> str:
           """Format code quality issue as GitHub Issue"""
   ```

**Deliverables:**
- `integrations/github_client.py` - GitHub API client
- `integrations/issue_templates.py` - Issue templates
- Configuration updates
- Unit tests (20+ tests)

**Success Criteria:**
- [ ] Successfully create issues via API
- [ ] Templates format issues correctly
- [ ] Attachments work (logs, screenshots)
- [ ] Labels applied correctly

#### Step 4.2: Agent Integration (Days 4-5)

**Tasks:**
1. **Update Bug Detection Agent**
   ```python
   # agents/phase3/bug_detection_agent.py
   
   def report_bug_to_github(self, bug_report: BugReport) -> Optional[str]:
       """Create GitHub Issue for detected bug"""
       if not self.github_integration_enabled:
           return None
       
       github_client = GitHubClient(self.config.github_token, self.config.github_repo)
       issue_body = IssueTemplate.bug_report(bug_report)
       
       issue_number = github_client.create_issue(IssueData(
           title=bug_report.title,
           body=issue_body,
           labels=['bug', 'automated', bug_report.severity]
       ))
       
       # Attach logs if available
       if bug_report.log_file:
           github_client.attach_file(issue_number, bug_report.log_file)
       
       # Get issue URL for return
       issue_url = github_client.get_issue_url(issue_number)
       return issue_url
   ```

2. **Update Performance Profiling Agent**
   ```python
   # agents/phase3/performance_profiling_agent.py
   
   def report_performance_issue(self, analysis: PerformanceAnalysis) -> Optional[str]:
       """Create GitHub Issue for performance regression"""
       # Similar to Bug Detection Agent
   ```

3. **Update Code Quality Agent**
   ```python
   # agents/phase3/code_quality_agent.py
   
   def report_critical_quality_issue(self, report: QualityReport) -> Optional[str]:
       """Create GitHub Issue for critical quality violations"""
       # Only for critical issues (score < 30)
   ```

**Deliverables:**
- Updated agents with GitHub integration
- Configuration options for enabling/disabling
- Integration tests (15+ tests)

**Success Criteria:**
- [ ] Agents create issues automatically
- [ ] Issues are well-formatted and actionable
- [ ] No duplicate issues created
- [ ] Users can disable GitHub integration

#### Step 4.3: CLI and Dashboard Updates (Days 6-7)

**Tasks:**
1. **Add GitHub Commands to Orchestrator CLI**
   ```bash
   # New commands:
   python agent_orchestrator_cli.py github status
   python agent_orchestrator_cli.py github configure
   python agent_orchestrator_cli.py github test
   ```

2. **Update Dashboard with GitHub Status**
   - Show "GitHub: Connected" status
   - Display recent issues created
   - Show issue creation rate

3. **Create GitHub Integration Guide**
   - Setup instructions
   - Token permissions guide
   - Issue template customization
   - Troubleshooting

**Deliverables:**
- CLI updates for GitHub commands
- Dashboard GitHub integration
- `docs/GITHUB_INTEGRATION.md` - Integration guide
- CLI tests (10+ tests)

**Success Criteria:**
- [ ] CLI commands work correctly
- [ ] Dashboard shows GitHub status
- [ ] Documentation is complete
- [ ] Integration is easy to setup

**Week 7 Completion Checklist:**
- [ ] GitHub API integration working
- [ ] All 3 agents create issues automatically
- [ ] CLI and dashboard updated
- [ ] 45+ new tests passing
- [ ] Documentation complete

---

### Week 8: Cost Tracking Implementation

**Goal:** Track and optimize OpenAI API costs across all agents.

**Priority:** MEDIUM - Controls operational costs

#### Step 5.1: Cost Tracker Core (Days 1-3)

**Tasks:**
1. **Update Cost Tracker**
   ```python
   # cost_tracker.py (already exists, needs enhancement)
   
   class CostTracker:
       def track_agent_call(self, agent_id: str, operation: str, 
                          tokens: int, cost: float) -> None:
           """Track API call by agent"""
       
       def get_session_cost(self, session_id: str) -> float:
           """Get cost for specific session"""
       
       def get_agent_costs(self, agent_id: str, 
                          start_date: datetime, end_date: datetime) -> AgentCostReport:
           """Get costs for specific agent"""
       
       def get_daily_cost(self, date: datetime) -> float:
           """Get total cost for a day"""
       
       def get_monthly_projection(self) -> float:
           """Project monthly cost based on current usage"""
       
       def check_budget_limit(self) -> BudgetStatus:
           """Check if approaching budget limit"""
       
       def export_cost_report(self, format: str) -> str:
           """Export cost report (CSV, JSON, PDF)"""
   ```

2. **Add Budget Management**
   ```python
   class BudgetManager:
       def set_daily_limit(self, limit: float) -> None
       def set_monthly_limit(self, limit: float) -> None
       def check_limit(self) -> BudgetAlert:
       def get_remaining_budget(self) -> float
   ```

3. **Create Cost Database**
   - SQLite database for cost history
   - Schema: session_id, agent_id, operation, tokens, cost, timestamp
   - Indexing for fast queries

**Deliverables:**
- Enhanced `cost_tracker.py`
- `budget_manager.py` - Budget management
- SQLite database schema
- Unit tests (30+ tests)

**Success Criteria:**
- [ ] Accurately tracks all API calls
- [ ] Budget limits work correctly
- [ ] Fast query performance (<100ms)
- [ ] All tests passing

#### Step 5.2: Agent Integration (Days 4-5)

**Tasks:**
1. **Update All Agents to Track Costs**
   ```python
   # agents/phase3/base_agent.py
   
   class BaseAutonomousAgent:
       def _track_llm_call(self, operation: str, 
                          prompt_tokens: int, completion_tokens: int) -> None:
           """
           Track LLM API call costs.
           
           Attempts to record the cost of an LLM API call for this agent.
           
           If cost tracking is disabled, this method does nothing.
           If an error occurs during cost tracking, the error is logged but not raised.
           
           Args:
               operation: Name of the operation (e.g., 'analyze_code').
               prompt_tokens: Number of tokens in the prompt.
               completion_tokens: Number of tokens in the completion.
           
           Raises:
               CostTrackingError: if tracking fails (logged but not raised).
           """
           total_tokens = prompt_tokens + completion_tokens
           cost = self._calculate_cost(prompt_tokens, completion_tokens)
           
           self.cost_tracker.track_agent_call(
               agent_id=self.agent_id,
               operation=operation,
               tokens=total_tokens,
               cost=cost
           )
           
           # Update agent metrics
           self.state.metrics.api_calls += 1
           self.state.metrics.tokens_used += total_tokens
   ```

2. **Add Cost Estimation**
   ```python
   def estimate_operation_cost(self, operation: str) -> CostEstimate:
       """
       Estimate the expected cost of an operation before execution.
       
       Args:
           operation: Name of the operation to estimate.
       
       Returns:
           CostEstimate: An object containing the expected cost and a confidence interval.
               The confidence interval is defined as ±20% of the expected cost, based on historical data for similar operations.
               If insufficient historical data is available, a default estimate is returned with a wider or unspecified confidence range.
       """
       # Based on historical data
       # Return estimate with confidence interval
   ```

3. **Implement Budget Checks**
   - Check budget before expensive operations
   - Alert user if operation would exceed budget
   - Option to proceed or cancel

**Deliverables:**
- Updated base agent with cost tracking
- Cost estimation for operations
- Integration tests (20+ tests)

**Success Criteria:**
- [ ] All agent API calls tracked
- [ ] Cost estimates within 10% of actual
- [ ] Budget checks prevent overruns
- [ ] No performance impact on agents

#### Step 5.3: CLI and Dashboard (Days 6-8)

**Tasks:**
1. **Add Cost Commands to CLI**
   ```bash
   # New commands:
   python agent_orchestrator_cli.py cost summary
   python agent_orchestrator_cli.py cost by-agent
   python agent_orchestrator_cli.py cost export --format csv
   python agent_orchestrator_cli.py cost set-budget --daily 10.0
   ```

2. **Create Cost Dashboard Panel**
   - Real-time cost display
   - Cost by agent (pie chart)
   - Daily/monthly trends
   - Budget remaining indicator
   - Alerts for approaching limits

3. **Add Cost Visualization**
   ```python
   # visualization/cost_visualizer.py
   
   class CostVisualizer:
       def generate_cost_chart(self, data: CostData) -> str:
           """Generate ASCII chart for terminal"""
       
       def export_cost_graph(self, data: CostData, format: str) -> str:
           """Export cost graph as PNG/SVG"""
   ```

**Deliverables:**
- CLI cost commands
- Dashboard cost panel
- Cost visualization
- CLI tests (15+ tests)
- Documentation updates

**Success Criteria:**
- [ ] CLI commands display costs correctly
- [ ] Dashboard shows real-time costs
- [ ] Visualizations are clear and useful
- [ ] Documentation complete

**Week 8 Completion Checklist:**
- [ ] Cost tracking operational across all agents
- [ ] Budget management working
- [ ] CLI and dashboard updated
- [ ] 65+ new tests passing
- [ ] Documentation complete with examples

---

### Week 9-10: Integration, Testing & Polish

**Goal:** Integrate all enhancements, comprehensive testing, and final polish.

**Priority:** CRITICAL - Ensures production readiness

#### Step 6.1: End-to-End Integration (Days 1-3)

**Tasks:**
1. **Full Integration Testing**
   - Test all 5 enhancements working together
   - UE Remote Control + Blueprint analysis + YAML validation + GitHub + Cost tracking
   - Identify integration issues
   - Fix conflicts and bugs

2. **Create Integration Test Suite**
   ```python
   # tests/integration/phase3/test_full_integration.py
   
   def test_complete_workflow():
       """Test complete Phase 3 workflow"""
       # 1. Connect to UE
       # 2. Start all agents
       # 3. Collect performance metrics
       # 4. Analyze Blueprint
       # 5. Generate and validate YAML
       # 6. Create GitHub issue
       # 7. Verify costs tracked
       # 8. Check all events published
   ```

3. **Performance Testing**
   - Measure agent response times
   - Check memory usage
   - Verify no memory leaks
   - Benchmark cost tracking overhead

**Deliverables:**
- Integration test suite (50+ tests)
- Performance benchmarks
- Bug fixes from integration testing

**Success Criteria:**
- [ ] All components work together seamlessly
- [ ] No integration bugs
- [ ] Performance meets targets (see ROADMAP.md)
- [ ] All integration tests pass

#### Step 6.2: Real-World Testing (Days 4-6)

**Tasks:**
1. **Test with Real Unreal Project**
   - Use actual UE game project
   - Run all agents for extended period (24+ hours)
   - Collect real performance data
   - Analyze real Blueprints
   - Create real GitHub issues
   - Track real costs

2. **Gather Feedback**
   - User acceptance testing
   - Performance evaluation
   - Usability assessment
   - Documentation review

3. **Fix Issues from Real-World Testing**
   - Address any bugs found
   - Improve error messages
   - Enhance usability
   - Optimize performance

**Deliverables:**
- Real-world test report
- Bug fixes and improvements
- User feedback incorporated

**Success Criteria:**
- [ ] System runs stably for 24+ hours
- [ ] All real-world scenarios work
- [ ] User feedback is positive
- [ ] No critical bugs

#### Step 6.3: Documentation Polish (Days 7-8)

**Tasks:**
1. **Update All Documentation**
   - PHASE3_GUIDE.md - Add all new features
   - ROADMAP.md - Mark Phase 3 as complete
   - README.md - Update Phase 3 status
   - Create PHASE3_COMPLETION.md

2. **Create New Documentation**
   - `docs/UNREAL_INTEGRATION_GUIDE.md` - Complete UE integration
   - `docs/BLUEPRINT_ANALYSIS_GUIDE.md` - Blueprint analysis
   - `docs/COST_OPTIMIZATION_GUIDE.md` - Cost tracking and optimization

3. **Video Demonstrations**
   - Record demo of all Phase 3 features
   - Upload to YouTube/project page
   - Add to documentation

**Deliverables:**
- Updated documentation (all files)
- New integration guides
- Video demonstrations
- PHASE3_COMPLETION.md

**Success Criteria:**
- [ ] All documentation up-to-date
- [ ] New guides complete and clear
- [ ] Video demonstrations available
- [ ] No documentation gaps

#### Step 6.4: Final Polish (Days 9-10)

**Tasks:**
1. **Code Cleanup**
   - Remove debug code
   - Clean up comments
   - Format all code consistently
   - Update type hints

2. **Final Testing**
   - Run full test suite (all 300+ tests)
   - Verify 100% pass rate
   - Check test coverage (>90% target)
   - Fix any remaining issues

3. **Prepare for Release**
   - Update version numbers
   - Create release notes
   - Tag release in git
   - Update CHANGELOG.md

**Deliverables:**
- Clean, polished code
- All tests passing
- Release notes
- Git tag for Phase 3 completion

**Success Criteria:**
- [ ] All 300+ tests passing
- [ ] Code coverage >90%
- [ ] No known critical bugs
- [ ] Ready for production use

**Week 9-10 Completion Checklist:**
- [ ] End-to-end integration complete
- [ ] Real-world testing successful
- [ ] All documentation updated
- [ ] Code polished and clean
- [ ] 50+ integration tests passing
- [ ] Phase 3 marked as COMPLETE

---

## Testing Strategy

### Test Coverage Goals

| Component | Target Coverage | Test Count |
|-----------|----------------|------------|
| Unreal Engine Integration | 90%+ | 70+ tests |
| Blueprint Support | 90%+ | 95+ tests |
| YAML Validation | 95%+ | 65+ tests |
| GitHub Integration | 90%+ | 60+ tests |
| Cost Tracking | 95%+ | 80+ tests |
| Integration Tests | N/A | 50+ tests |
| **Total New Tests** | | **420+ tests** |

### Testing Levels

1. **Unit Tests** - Test individual functions and classes
2. **Integration Tests** - Test component interactions
3. **End-to-End Tests** - Test complete workflows
4. **Real-World Tests** - Test with actual UE projects

---

## Success Metrics

### Phase 3 Complete Success Criteria

Per ROADMAP.md, Phase 3 is complete when:

| Metric | Target | Tracking |
|--------|--------|----------|
| Performance issues detected | 70%+ before human QA | Real-world testing |
| Bugs detected | 60%+ before manual testing | Real-world testing |
| Code quality issues identified | 80%+ of violations | Real-world testing |
| Blueprint complexity analysis | >80% accuracy | Validation tests |
| YAML generation validity | 100% valid | Validation tests |
| GitHub Issues automation | Working | Integration tests |
| Cost tracking accuracy | ±5% of actual | Monitoring |
| False positive rate | <10% | Real-world testing |
| Agent response time | <1 second for alerts | Performance tests |
| System uptime | 99%+ during development | Monitoring |
| Test pass rate | 100% | CI/CD |
| Test coverage | >90% | Coverage reports |

---

## Risk Management

### Identified Risks

1. **Unreal Engine Integration Complexity**
   - **Risk:** Remote Control API may be unreliable or limited
   - **Mitigation:** Extensive testing, fallback mechanisms, clear error messages
   - **Likelihood:** Medium
   - **Impact:** High

2. **Blueprint Parsing Challenges**
   - **Risk:** .uasset format may be difficult to parse
   - **Mitigation:** Use UE Python API instead of direct parsing
   - **Likelihood:** Medium
   - **Impact:** Medium

3. **API Cost Overruns**
   - **Risk:** Agents may consume more API tokens than budgeted
   - **Mitigation:** Cost tracking, budget limits, optimization
   - **Likelihood:** Low
   - **Impact:** Medium

4. **False Positives in Detection**
   - **Risk:** Agents may report non-issues
   - **Mitigation:** Tuning thresholds, machine learning, user feedback
   - **Likelihood:** Medium
   - **Impact:** Low

5. **Performance Degradation**
   - **Risk:** Agents may slow down development workflow
   - **Mitigation:** Async operations, background processing, optimization
   - **Likelihood:** Low
   - **Impact:** Medium

---

## Dependencies

### External Dependencies

1. **Unreal Engine 5.x** - For Remote Control API
2. **GitHub Account** - For Issues integration
3. **OpenAI API Key** - For LLM operations
4. **Python 3.9+** - Runtime environment

### Python Packages (New)

```txt
# requirements_phase3_enhancements.txt
jsonschema>=4.23.0     # YAML validation
PyGithub>=2.2.0,<3.0.0 # GitHub API
websockets>=12.0,<13.0 # WebSocket client
aiohttp>=3.9.0         # Async HTTP client
```

### Unreal Engine Plugins

1. **Web Remote Control Plugin** - Built-in, must be enabled
2. **Python Editor Script Plugin** - For Blueprint export

---

## Rollout Plan

### Phase 3 Enhancements Rollout

**Week 1-2:** UE Integration → **Early Access**
- Test with internal projects
- Gather initial feedback
- Fix critical bugs

**Week 6:** YAML Validation → **Beta Release**
- Announce to community
- Gather user feedback
- Monitor for issues

**Week 7:** GitHub Integration → **Beta Release**
- Document setup process
- Support users with issues

**Week 8:** Cost Tracking → **Beta Release**
- Monitor usage patterns
- Optimize based on data

**Week 10:** Full Integration → **Production Release**
- Announce Phase 3 completion
- Update marketplace listing (if applicable)
- Create release blog post

---

## Maintenance Plan

### Post-Completion Maintenance

**Monthly Tasks:**
- Review agent performance metrics
- Update documentation based on feedback
- Fix reported bugs
- Optimize cost usage

**Quarterly Tasks:**
- Major version updates
- Add new features based on feedback
- Refresh training data for agents
- Performance optimization

**Ongoing:**
- Monitor GitHub issues
- Respond to user questions
- Update for new UE versions
- Keep dependencies updated

---

## Appendix

### A. Detailed File Structure

```
adastrea-director/
├── agents/
│   ├── phase3/
│   │   ├── __init__.py
│   │   ├── base_agent.py (existing)
│   │   ├── performance_profiling_agent.py (existing)
│   │   ├── bug_detection_agent.py (existing)
│   │   ├── code_quality_agent.py (existing)
│   │   ├── event_bus.py (existing)
│   │   └── shared_state.py (existing)
│   └── blueprint/
│       ├── __init__.py (new)
│       ├── models.py (new)
│       ├── parser.py (new)
│       └── analyzer.py (new)
├── remote_control/
│   ├── __init__.py (new)
│   ├── http_client.py (new)
│   ├── websocket_client.py (new)
│   ├── manager.py (new)
│   └── models.py (new)
├── validation/
│   ├── __init__.py (new)
│   ├── schema_manager.py (new)
│   └── yaml_validator.py (new)
├── integrations/
│   ├── __init__.py (new)
│   ├── github_client.py (new)
│   └── issue_templates.py (new)
├── visualization/
│   ├── __init__.py (new)
│   └── cost_visualizer.py (new)
├── schemas/
│   ├── config_schema.json (new)
│   ├── data_table_schema.json (new)
│   └── ... (other YAML schemas)
├── scripts/
│   └── export_blueprint_data.py (new - UE Python)
├── tests/
│   ├── phase3/ (existing)
│   ├── integration/phase3/ (existing)
│   ├── blueprint/ (new)
│   ├── remote_control/ (new)
│   ├── validation/ (new)
│   └── integrations/ (new)
├── docs/
│   ├── UNREAL_REMOTE_CONTROL_SETUP.md (new)
│   ├── UNREAL_INTEGRATION_GUIDE.md (new)
│   ├── BLUEPRINT_ANALYSIS_GUIDE.md (new)
│   ├── BLUEPRINT_FORMAT.md (new)
│   ├── GITHUB_INTEGRATION.md (new)
│   └── COST_OPTIMIZATION_GUIDE.md (new)
├── cost_tracker.py (existing - needs enhancement)
├── budget_manager.py (new)
└── agent_orchestrator_cli.py (existing - needs updates)
```

### B. Configuration Examples

```yaml
# config/config.yaml - New sections

# Unreal Engine Integration
unreal_engine:
  enabled: true
  host: localhost
  http_port: 30010
  websocket_port: 30020
  auto_connect: false
  connection_timeout: 5

# Blueprint Analysis
blueprint:
  enabled: true
  complexity_threshold: 30
  max_node_count: 100
  detect_antipatterns: true

# YAML Validation
yaml_validation:
  enabled: true
  schema_dir: "./schemas"
  auto_fix: true
  fail_on_invalid: false

# GitHub Integration
github:
  enabled: false
  token: "${GITHUB_TOKEN}"
  repo: "owner/repo"
  auto_create_issues: true
  issue_labels:
    - "automated"
    - "adastrea-director"

# Cost Tracking
cost_tracking:
  enabled: true
  database: "./data/costs.db"
  daily_limit: 10.0
  monthly_limit: 300.0
  alert_threshold: 0.8
```

### C. Estimated Timeline Summary

| Week | Focus | Hours | Status |
|------|-------|-------|--------|
| 1-2 | UE Remote Control | 80 | ⏳ Not Started |
| 3-5 | Blueprint Support | 120 | ⏳ Not Started |
| 6 | YAML Validation | 40 | ⏳ Not Started |
| 7 | GitHub Integration | 40 | ⏳ Not Started |
| 8 | Cost Tracking | 40 | ⏳ Not Started |
| 9-10 | Integration & Polish | 80 | ⏳ Not Started |
| **Total** | | **400 hours** | |

**Note:** Hours are estimates. Actual time may vary based on complexity and unforeseen issues.

---

## Document Change History

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1.0 | 2025-11-19 | Initial creation | Copilot Agent |

---

**Next Action:** Begin Week 1-2 work on Unreal Engine Remote Control Integration

**Document Status:** ✅ Complete and Ready for Execution
