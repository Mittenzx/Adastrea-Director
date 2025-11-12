# Repository Structure and Relationship

This document clarifies the relationship between the Adastrea-Director repository and the game repository.

## Two Separate Repositories

### 1. Adastrea-Director (This Repository)
- **Purpose**: AI-powered development assistant and planning tool
- **Location**: `https://github.com/Mittenzx/Adastrea-Director`
- **Status**: Active development (currently Phase 2 complete)
- **Contains**: 
  - RAG system for document understanding
  - Planning agents for task decomposition
  - Code generation capabilities
  - GUI for interaction

### 2. Mittenzx/Adastrea (Game Repository)
- **Purpose**: The actual game being built
- **Location**: `https://github.com/Mittenzx/Adastrea` (private repository)
- **Status**: Active - Contains the game project
- **Contains**:
  - Unreal Engine 5 game project
  - C++ source code
  - Blueprints
  - Assets
  - Game design documents
  - Technical specifications
- **Access**: Private - Requires authentication

## How They Work Together

```
┌─────────────────────────┐
│  Adastrea-Director      │
│  (Planning Tool)        │
│  ┌──────────────────┐   │
│  │ Document Ingest  │───┼──► Can ingest docs from game repo
│  │ RAG System       │   │
│  │ Planning Agents  │   │
│  │ Code Generation  │   │
│  └──────────────────┘   │
└─────────────────────────┘
            │
            │ Provides assistance to
            │ developers working on
            ▼
┌─────────────────────────┐
│  Mittenzx/Adastrea      │
│  (Game Project)         │
│  ┌──────────────────┐   │
│  │ Unreal Engine 5  │   │
│  │ C++ Code         │   │
│  │ Blueprints       │   │
│  │ Assets           │   │
│  └──────────────────┘   │
└─────────────────────────┘
```

## Development Workflow

The Adastrea game repository exists and is actively being developed. To use Adastrea-Director with the game:

1. **Setup Access**: Ensure you have access to the private Mittenzx/Adastrea repository
2. **Get Credentials**: 
   - GitHub token with `repo` scope
   - OpenAI API key
3. **Ingest Game Docs**: Run `python ingest_game_repo.py` to load game documentation
4. **Use Director**: 
   - Use Adastrea-Director to understand the game codebase
   - Get AI assistance with development tasks
   - Generate code and plans for new features

## Testing Strategy

### Unit Tests
- Run against mock game repository structure
- Always available, no external dependencies
- Validate ingestion logic works correctly

### Integration Tests
- Test against the real private Mittenzx/Adastrea repository
- Require GitHub token with repo access and OpenAI API key
- Skip if credentials are not available or repository is inaccessible

### CI/CD Workflow
The `test-game-repo-integration.yml` workflow:
- ✅ Always runs unit tests with mock data (no credentials needed)
- ⚠️  Skips integration tests if secrets are not configured
- ✅ Runs full integration tests when GAME_REPO_TOKEN and OPENAI_API_KEY are available

## Using the Game Repository

To access and ingest from the private Mittenzx/Adastrea repository:

1. **Ensure you have access** - Contact repository owner if needed
2. **Add GitHub secrets** (for CI/CD, if not already done):
   - `GAME_REPO_TOKEN`: GitHub token with `repo` scope and access to Mittenzx/Adastrea
   - `OPENAI_API_KEY`: OpenAI API key
3. **Run ingestion locally**:
   ```bash
   export GITHUB_TOKEN="your_token"
   export OPENAI_API_KEY="your_key"
   python ingest_game_repo.py
   ```

## Alternative: Use a Different Game Repository

If you want to use Adastrea-Director with a different game project:

1. Update the repository URL in:
   - `ingest_game_repo.py` (line 55): `GAME_REPO_URL`
   - `tests/test_game_repo_ingestion.py` (line 30): `GAME_REPO_URL`

2. Run the ingestion script:
   ```bash
   python ingest_game_repo.py
   ```

3. Start using the Director with your game's context!

## Questions?

- **Is the game repository public?** No, Mittenzx/Adastrea is a private repository
- **Can I use this with other games?** Yes! Just update the repository URL
- **Will tests fail without access?** No, they skip gracefully with appropriate messages
- **How do I get access?** Contact the repository owner (Mittenzx)

---

**Last Updated**: 2025-11-12
