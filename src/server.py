"""
Skills MCP Server

A Model Context Protocol server that enables AI agents to discover, load,
and execute Agent Skills - organized folders of instructions, scripts, 
and resources that give agents additional capabilities.

Architecture:
- skill(name): Load a skill's full instructions (description includes ALL skills)
- execute_skill_script(skill_name, script_name, params): Run a skill's script
- get_skill_resource(skill_name, resource_path): Load reference docs or assets

Based on the Agent Skills specification: https://agentskills.io/specification

Author: YoruLabs
License: MIT
"""

import asyncio
import os
import json
import subprocess
import sys
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

import yaml
from mcp.server.fastmcp import FastMCP

# Configuration
SKILLS_DIR = os.environ.get("SKILLS_DIR", os.path.join(os.path.dirname(__file__), "..", "skills"))
Path(SKILLS_DIR).mkdir(parents=True, exist_ok=True)


def parse_skill_frontmatter(content: str) -> tuple[dict, str]:
    """
    Parse YAML frontmatter from SKILL.md content.
    
    Args:
        content: Full content of SKILL.md file
    
    Returns:
        Tuple of (frontmatter_dict, body_content)
    """
    frontmatter = {}
    body = content
    
    # Check for YAML frontmatter (content between --- markers)
    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            try:
                frontmatter = yaml.safe_load(parts[1]) or {}
                body = parts[2].strip()
            except yaml.YAMLError:
                pass
    
    return frontmatter, body


def get_skill_path(name: str) -> Path:
    """Get the full path for a skill directory."""
    # Sanitize the name to prevent directory traversal
    safe_name = "".join(c for c in name if c.isalnum() or c in "_-").lower()
    return Path(SKILLS_DIR) / safe_name


def validate_skill_name(name: str) -> tuple[bool, str]:
    """
    Validate skill name according to Agent Skills spec.
    
    Args:
        name: The skill name to validate
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not name:
        return False, "Name cannot be empty"
    
    if len(name) > 64:
        return False, "Name must be 64 characters or less"
    
    if not re.match(r'^[a-z0-9][a-z0-9-]*[a-z0-9]$|^[a-z0-9]$', name):
        return False, "Name must be lowercase alphanumeric with hyphens, cannot start/end with hyphen"
    
    if '--' in name:
        return False, "Name cannot contain consecutive hyphens"
    
    return True, ""


def list_skill_resources(skill_path: Path) -> dict:
    """
    List all resources available in a skill directory.
    
    Args:
        skill_path: Path to the skill directory
    
    Returns:
        Dict with scripts, references, and assets lists
    """
    resources = {
        "scripts": [],
        "references": [],
        "assets": []
    }
    
    scripts_dir = skill_path / "scripts"
    if scripts_dir.exists():
        resources["scripts"] = [f.name for f in scripts_dir.iterdir() if f.is_file()]
    
    references_dir = skill_path / "references"
    if references_dir.exists():
        resources["references"] = [f.name for f in references_dir.iterdir() if f.is_file()]
    
    assets_dir = skill_path / "assets"
    if assets_dir.exists():
        resources["assets"] = [f.name for f in assets_dir.iterdir() if f.is_file()]
    
    return resources


def get_all_skills_metadata() -> list[dict]:
    """
    Get metadata (name and description) for all available skills.
    
    Returns:
        List of dicts with name and description for each skill
    """
    skills = []
    skills_path = Path(SKILLS_DIR)
    
    if not skills_path.exists():
        return skills
    
    for skill_dir in sorted(skills_path.iterdir()):
        if not skill_dir.is_dir():
            continue
        
        skill_md = skill_dir / "SKILL.md"
        if not skill_md.exists():
            continue
        
        try:
            content = skill_md.read_text()
            frontmatter, _ = parse_skill_frontmatter(content)
            
            name = frontmatter.get("name", skill_dir.name)
            description = frontmatter.get("description", "No description provided")
            
            skills.append({
                "name": name,
                "description": description
            })
        except Exception:
            # Skip skills that can't be read
            continue
    
    return skills


def build_skill_tool_description() -> str:
    """
    Build the dynamic description for the skill tool that includes all available skills.
    
    Returns:
        Formatted description string with all skill names and descriptions
    """
    skills = get_all_skills_metadata()
    
    base_description = """Load a skill's full instructions and available resources.

This tool provides access to specialized skills that extend agent capabilities.
Each skill contains instructions, and optionally scripts, references, and assets.

"""
    
    if skills:
        base_description += "**Available skills:**\n"
        for skill in skills:
            # Truncate description if too long for the tool description
            desc = skill["description"]
            if len(desc) > 150:
                desc = desc[:147] + "..."
            base_description += f"- **{skill['name']}**: {desc}\n"
        base_description += "\n"
    else:
        base_description += "**No skills currently available.**\n\n"
    
    base_description += """After loading a skill, use `execute_skill_script()` to run any scripts,
or `get_skill_resource()` to load additional reference documents."""
    
    return base_description


# Initialize the MCP server
mcp = FastMCP("skills-mcp")


@mcp.tool()
def skill(name: str) -> dict:
    """
    Load a skill's full instructions and available resources.

    This tool provides access to specialized skills that extend agent capabilities.
    Each skill contains instructions, and optionally scripts, references, and assets.

    **Available skills:**
    (Skills are dynamically loaded - call this tool to see current skills)

    After loading a skill, use `execute_skill_script()` to run any scripts,
    or `get_skill_resource()` to load additional reference documents.
    
    Args:
        name: The skill name to load (e.g., "hello-world", "slack-message")
    
    Returns:
        dict: Skill metadata, full instructions, and available resources
    """
    try:
        # Validate name
        is_valid, error = validate_skill_name(name)
        if not is_valid:
            return {
                "status": "error",
                "message": f"Invalid skill name: {error}"
            }
        
        skill_path = get_skill_path(name)
        skill_md = skill_path / "SKILL.md"
        
        if not skill_path.exists() or not skill_md.exists():
            # Return available skills in error message
            available = get_all_skills_metadata()
            available_names = [s["name"] for s in available]
            return {
                "status": "error",
                "message": f"Skill '{name}' not found.",
                "available_skills": available_names
            }
        
        # Read and parse SKILL.md
        content = skill_md.read_text()
        frontmatter, body = parse_skill_frontmatter(content)
        
        result = {
            "status": "success",
            "name": frontmatter.get("name", name),
            "description": frontmatter.get("description", "No description"),
            "instructions": body,
            "resources": list_skill_resources(skill_path),
            "metadata": frontmatter.get("metadata", {}),
        }
        
        # Add optional fields if present
        if "license" in frontmatter:
            result["license"] = frontmatter["license"]
        
        if "compatibility" in frontmatter:
            result["compatibility"] = frontmatter["compatibility"]
        
        if "allowed-tools" in frontmatter:
            result["allowed_tools"] = frontmatter["allowed-tools"]
        
        # Add hints for next steps
        if result["resources"]["scripts"]:
            result["hint"] = f"Use execute_skill_script('{name}', '<script_name>', params) to run a script"
        
        return result
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to load skill: {str(e)}"
        }


# Update the skill tool's docstring dynamically at module load time
# This ensures the tool description always reflects current skills
def _update_skill_docstring():
    """Update the skill function's docstring with current skills."""
    skill.__doc__ = build_skill_tool_description() + """
    
    Args:
        name: The skill name to load (e.g., "hello-world", "slack-message")
    
    Returns:
        dict: Skill metadata, full instructions, and available resources
    """

_update_skill_docstring()


@mcp.tool()
def execute_skill_script(
    skill_name: str,
    script_name: str,
    params: dict = None
) -> dict:
    """
    Execute a script from a skill's scripts/ directory.
    
    Scripts are Python files that follow a standard format with a `run(params)` function.
    The script receives parameters as a dict and returns a dict result.
    
    Call `skill(name)` first to see available scripts for a skill.
    
    Args:
        skill_name: The skill name (e.g., "hello-world")
        script_name: The script filename (e.g., "greet.py")
        params: Optional dict of parameters to pass to the script
    
    Returns:
        dict: Script execution result with status and output
    
    Example:
        execute_skill_script("hello-world", "greet.py", {"name": "Alice"})
    """
    try:
        # Validate skill name
        is_valid, error = validate_skill_name(skill_name)
        if not is_valid:
            return {
                "status": "error",
                "message": f"Invalid skill name: {error}"
            }
        
        skill_path = get_skill_path(skill_name)
        
        if not skill_path.exists():
            return {
                "status": "error",
                "message": f"Skill '{skill_name}' not found"
            }
        
        # Sanitize script name
        if not script_name or ".." in script_name or "/" in script_name:
            return {
                "status": "error",
                "message": "Invalid script name"
            }
        
        script_path = skill_path / "scripts" / script_name
        
        if not script_path.exists():
            # List available scripts
            scripts_dir = skill_path / "scripts"
            available = []
            if scripts_dir.exists():
                available = [f.name for f in scripts_dir.iterdir() if f.is_file() and f.suffix == ".py"]
            
            return {
                "status": "error",
                "message": f"Script '{script_name}' not found in skill '{skill_name}'",
                "available_scripts": available
            }
        
        # Prepare parameters
        params = params or {}
        params_json = json.dumps(params)
        
        # Execute the script
        try:
            result = subprocess.run(
                [sys.executable, str(script_path), params_json],
                capture_output=True,
                text=True,
                timeout=60,  # 60 second timeout
                cwd=str(skill_path)
            )
            
            # Parse output
            if result.returncode == 0:
                try:
                    output = json.loads(result.stdout.strip()) if result.stdout.strip() else {}
                    return {
                        "status": "success",
                        "result": output
                    }
                except json.JSONDecodeError:
                    return {
                        "status": "success",
                        "result": {
                            "output": result.stdout.strip()
                        }
                    }
            else:
                return {
                    "status": "error",
                    "message": "Script execution failed",
                    "stderr": result.stderr,
                    "stdout": result.stdout,
                    "return_code": result.returncode
                }
        except subprocess.TimeoutExpired:
            return {
                "status": "error",
                "message": "Script execution timed out (60s limit)"
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Script execution error: {str(e)}"
            }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to execute script: {str(e)}"
        }


@mcp.tool()
def get_skill_resource(skill_name: str, resource_path: str) -> dict:
    """
    Load a specific resource file from a skill (reference docs, assets, etc.).
    
    Use this to load additional documentation or assets referenced in the skill's
    instructions. Resources are organized in directories:
    - references/ - Documentation, API specs, schemas
    - assets/ - Templates, data files, images
    - scripts/ - View script source code (use execute_skill_script to run)
    
    Args:
        skill_name: The skill name (e.g., "data-analysis")
        resource_path: Relative path to resource (e.g., "references/api.md")
    
    Returns:
        dict: Resource content and metadata
    
    Example:
        get_skill_resource("data-analysis", "references/schema.md")
    """
    try:
        # Validate skill name
        is_valid, error = validate_skill_name(skill_name)
        if not is_valid:
            return {
                "status": "error",
                "message": f"Invalid skill name: {error}"
            }
        
        skill_path = get_skill_path(skill_name)
        
        if not skill_path.exists():
            return {
                "status": "error",
                "message": f"Skill '{skill_name}' not found"
            }
        
        # Sanitize and validate resource path (prevent directory traversal)
        resource_path = resource_path.lstrip("/")
        if ".." in resource_path:
            return {
                "status": "error",
                "message": "Invalid resource path"
            }
        
        # Only allow access to specific directories
        allowed_prefixes = ["references/", "assets/", "scripts/"]
        if not any(resource_path.startswith(prefix) for prefix in allowed_prefixes):
            return {
                "status": "error",
                "message": f"Resource path must start with one of: {', '.join(allowed_prefixes)}"
            }
        
        full_path = skill_path / resource_path
        
        if not full_path.exists():
            # List available resources
            resources = list_skill_resources(skill_path)
            return {
                "status": "error",
                "message": f"Resource '{resource_path}' not found",
                "available_resources": resources
            }
        
        if not full_path.is_file():
            return {
                "status": "error",
                "message": "Path is not a file"
            }
        
        # Read the file
        try:
            content = full_path.read_text()
            return {
                "status": "success",
                "path": resource_path,
                "filename": full_path.name,
                "content": content,
                "size_bytes": len(content.encode('utf-8'))
            }
        except UnicodeDecodeError:
            # Binary file - return metadata only
            return {
                "status": "success",
                "path": resource_path,
                "filename": full_path.name,
                "content": "[Binary file - cannot display as text]",
                "size_bytes": full_path.stat().st_size,
                "is_binary": True
            }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to load resource: {str(e)}"
        }


def main():
    """Run the Skills MCP server."""
    # Update skill docstring before starting
    _update_skill_docstring()
    mcp.run()


if __name__ == "__main__":
    main()
