# Workflows MCP Server

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A Model Context Protocol (MCP) server that enables AI agents to programmatically create, manage, and execute independent Python workflow scripts. This provides a powerful, flexible, and vendor-agnostic way to automate tasks using AI.

Unlike platforms like Make or Dify, which only allow AI to *execute* pre-built workflows, this server empowers AI to **create and modify the workflows themselves** as simple Python scripts.

## Features

- **Programmatic Workflow Creation**: AI can generate new Python workflow scripts from scratch.
- **Independent Scripts**: Each workflow is a self-contained `.py` file, making them portable, versionable, and easy to debug.
- **Full Flexibility**: Leverage the entire Python ecosystem within your workflows.
- **Simple Execution**: Run any workflow by name with optional parameters.
- **Full CRUD Operations**: Create, Read, Update, and Delete workflows via MCP tools.
- **Vendor-Agnostic**: Built on the open Model Context Protocol standard.

## Getting Started

### Prerequisites

- Python 3.10+
- An MCP-compatible client (e.g., Manus, Cursor, LobeChat)

### Installation

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/YoruLabs/Workflows-MCP.git
    cd Workflows-MCP
    ```

2.  **Install dependencies:**

    ```bash
    pip install -e .
    ```

3.  **Run the server:**

    ```bash
    workflows-mcp
    ```

    The server will start and be available for your MCP client to connect to.

### Configuration

- **Workflows Directory**: By default, workflows are stored in the `workflows/` directory. You can change this by setting the `WORKFLOWS_DIR` environment variable.
- **Slack Webhook**: For the `example_slack_message` workflow, set the `SLACK_WEBHOOK_URL` environment variable.

## MCP Tools

The server exposes the following tools for AI agents:

| Tool Name | Description |
| :--- | :--- |
| `create_workflow` | Creates a new Python workflow script from a name, description, and code. |
| `execute_workflow` | Executes a workflow by name, passing optional JSON parameters. |
| `list_workflows` | Lists all available workflow scripts with their metadata. |
| `read_workflow` | Reads the full source code of a specified workflow script. |
| `update_workflow` | Updates the description or code of an existing workflow. |
| `delete_workflow` | Deletes a workflow script from the filesystem. |

## Creating a Workflow

To create a workflow, the AI agent calls the `create_workflow` tool. The `code` parameter must contain a Python script with a `run` function.

**Example `run` function:**

```python
def run(params: dict = None) -> dict:
    """
    This is the entry point for the workflow.
    
    Args:
        params: An optional dictionary of parameters passed during execution.
    
    Returns:
        A dictionary with the results of the workflow.
    """
    params = params or {}
    name = params.get("name", "World")
    
    # ... your workflow logic ...
    
    return {"status": "success", "greeting": f"Hello, {name}!"}
```

## Example Workflows

This repository includes two example workflows in the `workflows/` directory:

1.  `example_hello_world.py`: A simple workflow that takes a `name` and `uppercase` parameter and returns a greeting.
2.  `example_slack_message.py`: A workflow that posts a message to a Slack channel using a webhook URL.

## Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
