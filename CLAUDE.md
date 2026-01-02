# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

Skills MCP Server is a Model Context Protocol (MCP) server that enables AI agents to discover, load, and execute **Agent Skills** - organized folders of instructions, scripts, and resources that give agents additional capabilities.

Based on the [Agent Skills specification](https://agentskills.io/specification).

## Development Commands

### Installation and Setup
```bash
# Install in editable mode with dependencies
pip install -e .

# Install with development dependencies
pip install -e ".[dev]"
```

### Running the Server
```bash
# Run the MCP server
skills-mcp

# Run with custom skills directory
SKILLS_DIR=/path/to/skills skills-mcp
```

### Testing
```bash
# Run tests
pytest

# Run tests with async support
pytest -v

# Test a skill script directly
python skills/hello-world/scripts/greet.py '{"name": "Alice"}'
```

### Code Quality
```bash
# Format code with black
black src/ skills/

# Lint with ruff
ruff check src/ skills/
```

## Architecture

### 3-Tool Progressive Disclosure Model

The server exposes exactly **3 MCP tools** that implement progressive disclosure:

1. **`skill(name)`** - Loads a skill's full instructions
   - Tool description is **dynamically generated** to include ALL skill names and descriptions
   - Agents see all available skills without making any tool calls
   - Returns full SKILL.md content and available resources

2. **`execute_skill_script(skill_name, script_name, params)`** - Executes Python scripts
   - Scripts run in subprocess with 60s timeout
   - Scripts receive params as JSON string via sys.argv[1]
   - Must return valid JSON with at minimum a `status` field

3. **`get_skill_resource(skill_name, resource_path)`** - Loads reference docs/assets
   - Only allows access to `references/`, `assets/`, and `scripts/` directories
   - Prevents directory traversal attacks
   - Returns text content or binary file metadata

### Progressive Loading (3 Levels)

Skills use progressive disclosure to manage context efficiently:

- **Level 1**: Name + description (always visible in `skill` tool description)
- **Level 2**: Full SKILL.md loaded when `skill(name)` is called
- **Level 3**: Scripts/references loaded when `execute_skill_script()` or `get_skill_resource()` is called

### Key Implementation Details

**Dynamic Tool Descriptions** (src/server.py:165-196):
- `build_skill_tool_description()` generates the `skill` tool description at runtime
- Scans all skills in `SKILLS_DIR` and embeds their names and descriptions
- `_update_skill_docstring()` updates the tool docstring before server starts

**Skill Discovery** (src/server.py:126-162):
- `get_all_skills_metadata()` scans the skills directory at startup
- Only reads YAML frontmatter (name + description) from each SKILL.md
- Invalid skills are silently skipped to prevent server startup failures

**Script Execution** (src/server.py:296-411):
- Scripts run via subprocess with JSON params passed as command-line argument
- 60-second timeout enforced
- Working directory is set to the skill directory
- Expects scripts to output valid JSON to stdout

**Security Measures** (throughout src/server.py):
- Skill name validation: lowercase alphanumeric with hyphens only, 1-64 chars
- Path sanitization prevents directory traversal (`..` blocked)
- Resource access restricted to `scripts/`, `references/`, `assets/` directories

## Skill Structure

Every skill follows the Agent Skills specification:

```
skills/
└── skill-name/
    ├── SKILL.md              # Required: YAML frontmatter + markdown body
    ├── scripts/              # Optional: Python scripts with run(params) -> dict
    ├── references/           # Optional: Docs loaded on-demand into context
    └── assets/               # Optional: Files used in output (not loaded into context)
```

### SKILL.md Requirements

**Frontmatter (YAML):**
- `name` (required): Must match directory name, follow naming conventions
- `description` (required): 1-1024 chars, describes what skill does AND when to use it
- `license` (optional): e.g., "MIT"
- `metadata` (optional): author, version, etc.

**Body (Markdown):**
- Full instructions for using the skill
- Only loaded after `skill(name)` is called
- Keep under 5000 tokens / 500 lines

### Script Requirements

All scripts must follow this format:

```python
import sys
import json

def run(params: dict = None) -> dict:
    """Entry point. Must return dict with at minimum 'status' field."""
    params = params or {}
    # Your logic here
    return {"status": "success", "result": "..."}

if __name__ == "__main__":
    params = {}
    if len(sys.argv) > 1:
        params = json.loads(sys.argv[1])
    result = run(params)
    print(json.dumps(result))
```

## Creating New Skills

Follow the workflow in SKILL_CREATION.md:

1. **Understand** - Collect concrete examples of how the skill will be used
2. **Plan** - Identify what scripts/references/assets would be helpful
3. **Create** - Set up directory structure with proper SKILL.md frontmatter
4. **Implement** - Write scripts and references
5. **Test** - Run scripts directly to verify output
6. **Validate** - Check naming, frontmatter, script format
7. **Iterate** - Use in real tasks and refine

### Design Principles

**Concise is Key**: Context window is shared. Only include what the agent doesn't already know.

**Set Appropriate Degrees of Freedom**:
- High (text instructions): Multiple approaches valid, context-dependent decisions
- Medium (pseudocode): Preferred pattern exists, some variation acceptable
- Low (specific scripts): Operations fragile, consistency critical

**Progressive Disclosure**: Keep SKILL.md under 500 lines. Split detailed content into references.

## Configuration

**Environment Variables:**
- `SKILLS_DIR` - Path to skills directory (default: `./skills`)

**Project Structure:**
- `src/server.py` - Main MCP server implementation (520 lines)
- `skills/` - Skill packages following Agent Skills specification
- `pyproject.toml` - Package configuration, dependencies, tooling config

## Important Notes

- Skills are discovered at server startup by scanning `SKILLS_DIR`
- The `skill` tool description is regenerated on each server start
- Skills with invalid frontmatter are silently skipped
- All script execution is sandboxed with 60s timeout
- Binary files in resources return metadata only, not content
