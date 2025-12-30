# Skills MCP Server

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A Model Context Protocol (MCP) server that enables AI agents to discover, load, and execute **Agent Skills** - organized folders of instructions, scripts, and resources that give agents additional capabilities.

Based on the [Agent Skills specification](https://agentskills.io/specification).

## What are Skills?

Skills are folders containing:
- **SKILL.md** - Instructions and metadata (name, description)
- **scripts/** - Executable Python scripts
- **references/** - Additional documentation (loaded on demand)
- **assets/** - Static resources (templates, data files)

Skills use **progressive disclosure** to efficiently manage context:
1. **Level 1**: Name + description always visible in the `skill` tool description
2. **Level 2**: Full SKILL.md loaded when `skill(name)` is called
3. **Level 3**: Scripts/references loaded when `execute_skill_script()` or `get_skill_resource()` is called

## Features

- **Dynamic Skill Discovery**: All skill names and descriptions are embedded in the `skill` tool description
- **Progressive Loading**: Load skill instructions on demand
- **Script Execution**: Run pre-built Python scripts from skills
- **Resource Access**: Load reference docs and assets as needed
- **Agent Skills Compatible**: Follows the open Agent Skills specification

## Getting Started

### Prerequisites

- Python 3.10+
- An MCP-compatible client (e.g., Manus, Claude Code, Cursor)

### Installation

1. **Clone the repository:**

    ```bash
    git clone https://github.com/Livus-AI/Skills-MCP.git
    cd Skills-MCP
    ```

2. **Install dependencies:**

    ```bash
    pip install -e .
    ```

3. **Run the server:**

    ```bash
    skills-mcp
    ```

### Configuration

- **Skills Directory**: By default, skills are stored in the `skills/` directory. You can change this by setting the `SKILLS_DIR` environment variable.

## MCP Tools

The server exposes **3 tools**:

| Tool | Description |
| :--- | :--- |
| `skill(name)` | Load a skill's full instructions. **The tool description dynamically includes ALL skill names and descriptions.** |
| `execute_skill_script(skill_name, script_name, params)` | Execute a Python script from a skill's `scripts/` directory. |
| `get_skill_resource(skill_name, resource_path)` | Load a specific resource file (reference docs, assets). |

### How It Works

The `skill` tool description is **dynamically generated** to always include the name and description of every available skill. This means:

1. **Agents see all skills immediately** - No need to call a "list" function
2. **One call to load** - `skill("name")` loads full instructions
3. **Execute when ready** - `execute_skill_script()` runs scripts

### Example Workflow

```
# Agent reads skill tool description and sees:
# - hello-world: A simple example skill...
# - slack-message: Post messages to Slack...

# Step 1: Load the skill
skill("slack-message")
# Returns: full instructions, available scripts, resources

# Step 2: Execute a script
execute_skill_script("slack-message", "post.py", {"channel": "#general", "message": "Hello!"})
# Returns: script output
```

## Creating a Skill

See [SKILL_CREATION.md](SKILL_CREATION.md) for the complete guide.

### Quick Start

1. **Create the directory structure:**

```
skills/
└── my-skill/
    ├── SKILL.md              # Required: Instructions + metadata
    ├── scripts/              # Optional: Executable scripts
    │   └── main.py
    ├── references/           # Optional: Additional docs
    │   └── api.md
    └── assets/               # Optional: Static resources
        └── template.json
```

2. **Create SKILL.md with frontmatter:**

```yaml
---
name: my-skill
description: What this skill does and when to use it. Include keywords that help agents identify relevant tasks.
license: MIT
metadata:
  author: your-name
  version: "1.0"
---

# My Skill

## Overview
Brief description of what this skill helps accomplish.

## Available Scripts
- `scripts/main.py` - Primary functionality

## How to Use
Step-by-step instructions...
```

3. **Create scripts with the standard format:**

```python
import sys
import json

def run(params: dict = None) -> dict:
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

## Example Skills

This repository includes example skills in the `skills/` directory:

1. **hello-world** - A simple example demonstrating the skill format
2. **slack-message** - Post messages to Slack via webhook

## Roadmap

- [ ] `create_skill` tool - Create new skills programmatically
- [ ] `execute_code` tool - Execute arbitrary Python code with e2b sandboxing
- [ ] Skill validation and linting
- [ ] Skill versioning and updates

## Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Related

- [Agent Skills Specification](https://agentskills.io/specification)
- [Anthropic Skills Repository](https://github.com/anthropics/skills)
- [Model Context Protocol](https://modelcontextprotocol.io)
