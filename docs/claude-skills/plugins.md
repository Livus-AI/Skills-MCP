# Create plugins

> Create custom plugins to extend Claude Code with slash commands, agents, hooks, Skills, and MCP servers.

Plugins let you extend Claude Code with custom functionality that can be shared across projects and teams. This guide covers creating your own plugins with slash commands, agents, Skills, hooks, and MCP servers.

Looking to install existing plugins? See [Discover and install plugins](/en/discover-plugins). For complete technical specifications, see [Plugins reference](/en/plugins-reference).

## When to use plugins vs standalone configuration

Claude Code supports two ways to add custom slash commands, agents, and hooks:

| Approach                                                    | Slash command names  | Best for                                                                                        |
| :---------------------------------------------------------- | :------------------- | :---------------------------------------------------------------------------------------------- |
| **Standalone** (`.claude/` directory)                       | `/hello`             | Personal workflows, project-specific customizations, quick experiments                          |
| **Plugins** (directories with `.claude-plugin/plugin.json`) | `/plugin-name:hello` | Sharing with teammates, distributing to community, versioned releases, reusable across projects |

**Use standalone configuration when**:

* You're customizing Claude Code for a single project
* The configuration is personal and doesn't need to be shared
* You're experimenting with slash commands or hooks before packaging them
* You want short slash command names like `/hello` or `/review`

**Use plugins when**:

* You want to share functionality with your team or community
* You need the same slash commands/agents across multiple projects
* You want version control and easy updates for your extensions
* You're distributing through a marketplace
* You're okay with namespaced slash commands like `/my-plugin:hello` (namespacing prevents conflicts between plugins)

<Tip>
  Start with standalone configuration in `.claude/` for quick iteration, then [convert to a plugin](#convert-existing-configurations-to-plugins) when you're ready to share.
</Tip>

## Quickstart

This quickstart walks you through creating a plugin with a custom slash command. You'll create a manifest (the configuration file that defines your plugin), add a slash command, and test it locally using the `--plugin-dir` flag.

### Prerequisites

* Claude Code [installed and authenticated](/en/quickstart#step-1-install-claude-code)
* Claude Code version 1.0.33 or later (run `claude --version` to check)

<Note>
  If you don't see the `/plugin` command, update Claude Code to the latest version. See [Troubleshooting](/en/troubleshooting) for upgrade instructions.
</Note>

### Create your first plugin

<Steps>
  <Step title="Create the plugin directory">
    Every plugin lives in its own directory containing a manifest and your custom commands, agents, or hooks. Create one now:

    ```bash  theme={null}
    mkdir my-first-plugin
    ```
  </Step>

  <Step title="Create the plugin manifest">
    The manifest file at `.claude-plugin/plugin.json` defines your plugin's identity: its name, description, and version. Claude Code uses this metadata to display your plugin in the plugin manager.

    Create the `.claude-plugin` directory inside your plugin folder:

    ```bash  theme={null}
    mkdir my-first-plugin/.claude-plugin
    ```

    Then create `my-first-plugin/.claude-plugin/plugin.json` with this content:

    ```json my-first-plugin/.claude-plugin/plugin.json theme={null}
    {
    "name": "my-first-plugin",
    "description": "A greeting plugin to learn the basics",
    "version": "1.0.0",
    "author": {
    "name": "Your Name"
    }
    }
    ```

    | Field         | Purpose                                                                                                                |
    | :------------ | :--------------------------------------------------------------------------------------------------------------------- |
    | `name`        | Unique identifier and slash command namespace. Slash commands are prefixed with this (e.g., `/my-first-plugin:hello`). |
    | `description` | Shown in the plugin manager when browsing or installing plugins.                                                       |
    | `version`     | Track releases using [semantic versioning](/en/plugins-reference#version-management).                                  |
    | `author`      | Optional. Helpful for attribution.                                                                                     |

    For additional fields like `homepage`, `repository`, and `license`, see the [full manifest schema](/en/plugins-reference#plugin-manifest-schema).
  </Step>

  <Step title="Add a slash command">
    Slash commands are Markdown files in the `commands/` directory. The filename becomes the slash command name, prefixed with the plugin's namespace (`hello.md` in a plugin named `my-first-plugin` creates `/my-first-plugin:hello`). The Markdown content tells Claude how to respond when someone runs the slash command.

    Create a `commands` directory in your plugin folder:

    ```bash  theme={null}
    mkdir my-first-plugin/commands
    ```

    Then create `my-first-plugin/commands/hello.md` with this content:

    ```markdown my-first-plugin/commands/hello.md theme={null}
    ---
    description: Greet the user with a friendly message
    ---

    # Hello Command

    Greet the user warmly and ask how you can help them today.
    ```
  </Step>

  <Step title="Test your plugin">
    Run Claude Code with the `--plugin-dir` flag to load your plugin:

    ```bash  theme={null}
    claude --plugin-dir ./my-first-plugin
    ```

    Once Claude Code starts, try your new command:

    ```shell  theme={null}
    /my-first-plugin:hello
    ```

    You'll see Claude respond with a greeting. Run `/help` to see your command listed under the plugin namespace.

    <Note>
      **Why namespacing?** Plugin slash commands are always namespaced (like `/greet:hello`) to prevent conflicts when multiple plugins have commands with the same name.

      To change the namespace prefix, update the `name` field in `plugin.json`.
    </Note>
  </Step>

  <Step title="Add slash command arguments">
    Make your slash command dynamic by accepting user input. The `$ARGUMENTS` placeholder captures any text the user provides after the slash command.

    Update your `hello.md` file:

    ```markdown my-first-plugin/commands/hello.md theme={null}
    ---
    description: Greet the user with a personalized message
    ---

    # Hello Command

    Greet the user named "$ARGUMENTS" warmly and ask how you can help them today. Make the greeting personal and encouraging.
    ```

    Restart Claude Code to pick up the changes, then try the command with your name:

    ```shell  theme={null}
    /my-first-plugin:hello Alex
    ```

    Claude will greet you by name. For more argument options like `$1`, `$2` for individual parameters, see [Slash commands](/en/slash-commands).
  </Step>
</Steps>

You've successfully created and tested a plugin with these key components:

* **Plugin manifest** (`.claude-plugin/plugin.json`): describes your plugin's metadata
* **Commands directory** (`commands/`): contains your custom slash commands
* **Command arguments** (`$ARGUMENTS`): captures user input for dynamic behavior

<Tip>
  The `--plugin-dir` flag is useful for development and testing. When you're ready to share your plugin with others, see [Create and distribute a plugin marketplace](/en/plugin-marketplaces).
</Tip>

## Plugin structure overview

You've created a plugin with a slash command, but plugins can include much more: custom agents, Skills, hooks, MCP servers, and LSP servers.

<Warning>
  **Common mistake**: Don't put `commands/`, `agents/`, `skills/`, or `hooks/` inside the `.claude-plugin/` directory. Only `plugin.json` goes inside `.claude-plugin/`. All other directories must be at the plugin root level.
</Warning>

| Directory         | Location    | Purpose                                         |
| :---------------- | :---------- | :---------------------------------------------- |
| `.claude-plugin/` | Plugin root | Contains only `plugin.json` manifest (required) |
| `commands/`       | Plugin root | Slash commands as Markdown files                |
| `agents/`         | Plugin root | Custom agent definitions                        |
| `skills/`         | Plugin root | Agent Skills with `SKILL.md` files              |
| `hooks/`          | Plugin root | Event handlers in `hooks.json`                  |
| `.mcp.json`       | Plugin root | MCP server configurations                       |
| `.lsp.json`       | Plugin root | LSP server configurations for code intelligence |

<Note>
  **Next steps**: Ready to add more features? Jump to [Develop more complex plugins](#develop-more-complex-plugins) to add agents, hooks, MCP servers, and LSP servers. For complete technical specifications of all plugin components, see [Plugins reference](/en/plugins-reference).
</Note>

## Develop more complex plugins

Once you're comfortable with basic plugins, you can create more sophisticated extensions.

### Add Skills to your plugin

Plugins can include [Agent Skills](/en/skills) to extend Claude's capabilities. Skills are model-invoked: Claude automatically uses them based on the task context.

Add a `skills/` directory at your plugin root with Skill folders containing `SKILL.md` files:

```
my-plugin/
├── .claude-plugin/
│   └── plugin.json
└── skills/
    └── code-review/
        └── SKILL.md
```

Each `SKILL.md` needs frontmatter with `name` and `description` fields, followed by instructions:

```yaml  theme={null}
---
name: code-review
description: Reviews code for best practices and potential issues. Use when reviewing code, checking PRs, or analyzing code quality.
---

When reviewing code, check for:
1. Code organization and structure
2. Error handling
3. Security concerns
4. Test coverage
```

After installing the plugin, restart Claude Code to load the Skills. For complete Skill authoring guidance including progressive disclosure and tool restrictions, see [Agent Skills](/en/skills).

### Add LSP servers to your plugin

<Tip>
  For common languages like TypeScript, Python, and Rust, install the pre-built LSP plugins from the official marketplace. Create custom LSP plugins only when you need support for languages not already covered.
</Tip>

LSP (Language Server Protocol) plugins give Claude real-time code intelligence. If you need to support a language that doesn't have an official LSP plugin, you can create your own by adding an `.lsp.json` file to your plugin:

```json .lsp.json theme={null}
{
  "go": {
    "command": "gopls",
    "args": ["serve"],
    "extensionToLanguage": {
      ".go": "go"
    }
  }
}
```

Users installing your plugin must have the language server binary installed on their machine.

For complete LSP configuration options, see [LSP servers](/en/plugins-reference#lsp-servers).

### Organize complex plugins

For plugins with many components, organize your directory structure by functionality. For complete directory layouts and organization patterns, see [Plugin directory structure](/en/plugins-reference#plugin-directory-structure).

### Test your plugins locally

Use the `--plugin-dir` flag to test plugins during development. This loads your plugin directly without requiring installation.

```bash  theme={null}
claude --plugin-dir ./my-plugin
```

As you make changes to your plugin, restart Claude Code to pick up the updates. Test your plugin components:

* Try your commands with `/command-name`
* Check that agents appear in `/agents`
* Verify hooks work as expected

<Tip>
  You can load multiple plugins at once by specifying the flag multiple times:

  ```bash  theme={null}
  claude --plugin-dir ./plugin-one --plugin-dir ./plugin-two
  ```
</Tip>

### Debug plugin issues

If your plugin isn't working as expected:

1. **Check the structure**: Ensure your directories are at the plugin root, not inside `.claude-plugin/`
2. **Test components individually**: Check each command, agent, and hook separately
3. **Use validation and debugging tools**: See [Debugging and development tools](/en/plugins-reference#debugging-and-development-tools) for CLI commands and troubleshooting techniques

### Share your plugins

When your plugin is ready to share:

1. **Add documentation**: Include a `README.md` with installation and usage instructions
2. **Version your plugin**: Use [semantic versioning](/en/plugins-reference#version-management) in your `plugin.json`
3. **Create or use a marketplace**: Distribute through [plugin marketplaces](/en/plugin-marketplaces) for installation
4. **Test with others**: Have team members test the plugin before wider distribution

Once your plugin is in a marketplace, others can install it using the instructions in [Discover and install plugins](/en/discover-plugins).

<Note>
  For complete technical specifications, debugging techniques, and distribution strategies, see [Plugins reference](/en/plugins-reference).
</Note>

## Convert existing configurations to plugins

If you already have custom commands, Skills, or hooks in your `.claude/` directory, you can convert them into a plugin for easier sharing and distribution.

### Migration steps

<Steps>
  <Step title="Create the plugin structure">
    Create a new plugin directory:

    ```bash  theme={null}
    mkdir -p my-plugin/.claude-plugin
    ```

    Create the manifest file at `my-plugin/.claude-plugin/plugin.json`:

    ```json my-plugin/.claude-plugin/plugin.json theme={null}
    {
      "name": "my-plugin",
      "description": "Migrated from standalone configuration",
      "version": "1.0.0"
    }
    ```
  </Step>

  <Step title="Copy your existing files">
    Copy your existing configurations to the plugin directory:

    ```bash  theme={null}
    # Copy commands
    cp -r .claude/commands my-plugin/

    # Copy agents (if any)
    cp -r .claude/agents my-plugin/

    # Copy skills (if any)
    cp -r .claude/skills my-plugin/
    ```
  </Step>

  <Step title="Migrate hooks">
    If you have hooks in your settings, create a hooks directory:

    ```bash  theme={null}
    mkdir my-plugin/hooks
    ```

    Create `my-plugin/hooks/hooks.json` with your hooks configuration. Copy the `hooks` object from your `.claude/settings.json` or `settings.local.json`—the format is the same:

    ```json my-plugin/hooks/hooks.json theme={null}
    {
      "hooks": {
        "PostToolUse": [
          {
            "matcher": "Write|Edit",
            "hooks": [{ "type": "command", "command": "npm run lint:fix $FILE" }]
          }
        ]
      }
    }
    ```
  </Step>

  <Step title="Test your migrated plugin">
    Load your plugin to verify everything works:

    ```bash  theme={null}
    claude --plugin-dir ./my-plugin
    ```

    Test each component: run your commands, check agents appear in `/agents`, and verify hooks trigger correctly.
  </Step>
</Steps>

### What changes when migrating

| Standalone (`.claude/`)       | Plugin                           |
| :---------------------------- | :------------------------------- |
| Only available in one project | Can be shared via marketplaces   |
| Files in `.claude/commands/`  | Files in `plugin-name/commands/` |
| Hooks in `settings.json`      | Hooks in `hooks/hooks.json`      |
| Must manually copy to share   | Install with `/plugin install`   |

<Note>
  After migrating, you can remove the original files from `.claude/` to avoid duplicates. The plugin version will take precedence when loaded.
</Note>

## Next steps

Now that you understand Claude Code's plugin system, here are suggested paths for different goals:

### For plugin users

* [Discover and install plugins](/en/discover-plugins): browse marketplaces and install plugins
* [Configure team marketplaces](/en/discover-plugins#configure-team-marketplaces): set up repository-level plugins for your team

### For plugin developers

* [Create and distribute a marketplace](/en/plugin-marketplaces): package and share your plugins
* [Plugins reference](/en/plugins-reference): complete technical specifications
* Dive deeper into specific plugin components:
  * [Slash commands](/en/slash-commands): command development details
  * [Subagents](/en/sub-agents): agent configuration and capabilities
  * [Agent Skills](/en/skills): extend Claude's capabilities
  * [Hooks](/en/hooks): event handling and automation
  * [MCP](/en/mcp): external tool integration


---

> To find navigation and other pages in this documentation, fetch the llms.txt file at: https://code.claude.com/docs/llms.txt

# Discover and install prebuilt plugins through marketplaces

> Find and install plugins from marketplaces to extend Claude Code with new commands, agents, and capabilities.

Plugins extend Claude Code with custom commands, agents, hooks, and MCP servers. Plugin marketplaces are catalogs that help you discover and install these extensions without building them yourself.

Looking to create and distribute your own marketplace? See [Create and distribute a plugin marketplace](/en/plugin-marketplaces).

## How marketplaces work

A marketplace is a catalog of plugins that someone else has created and shared. Using a marketplace is a two-step process:

<Steps>
  <Step title="Add the marketplace">
    This registers the catalog with Claude Code so you can browse what's available. No plugins are installed yet.
  </Step>

  <Step title="Install individual plugins">
    Browse the catalog and install the plugins you want.
  </Step>
</Steps>

Think of it like adding an app store: adding the store gives you access to browse its collection, but you still choose which apps to download individually.

## Official Anthropic marketplace

The official Anthropic marketplace (`claude-plugins-official`) is automatically available when you start Claude Code. Run `/plugin` and go to the **Discover** tab to browse what's available.

To install a plugin from the official marketplace:

```shell  theme={null}
/plugin install plugin-name@claude-plugins-official
```

<Note>
  The official marketplace is maintained by Anthropic. To distribute your own plugins, [create your own marketplace](/en/plugin-marketplaces) and share it with users.
</Note>

The official marketplace includes several categories of plugins:

### Code intelligence

Code intelligence plugins help Claude understand your codebase more deeply. With these plugins installed, Claude can jump to definitions, find references, and see type errors immediately after edits. These plugins use the [Language Server Protocol](https://microsoft.github.io/language-server-protocol/) (LSP), the same technology that powers VS Code's code intelligence.

These plugins require the language server binary to be installed on your system. If you already have a language server installed, Claude may prompt you to install the corresponding plugin when you open a project.

| Language   | Plugin              | Binary required              |
| :--------- | :------------------ | :--------------------------- |
| C/C++      | `clangd-lsp`        | `clangd`                     |
| C#         | `csharp-lsp`        | `csharp-ls`                  |
| Go         | `gopls-lsp`         | `gopls`                      |
| Java       | `jdtls-lsp`         | `jdtls`                      |
| Lua        | `lua-lsp`           | `lua-language-server`        |
| PHP        | `php-lsp`           | `intelephense`               |
| Python     | `pyright-lsp`       | `pyright-langserver`         |
| Rust       | `rust-analyzer-lsp` | `rust-analyzer`              |
| Swift      | `swift-lsp`         | `sourcekit-lsp`              |
| TypeScript | `typescript-lsp`    | `typescript-language-server` |

You can also [create your own LSP plugin](/en/plugins-reference#lsp-servers) for other languages.

<Note>
  If you see `Executable not found in $PATH` in the `/plugin` Errors tab after installing a plugin, install the required binary from the table above.
</Note>

### External integrations

These plugins bundle pre-configured [MCP servers](/en/mcp) so you can connect Claude to external services without manual setup:

* **Source control**: `github`, `gitlab`
* **Project management**: `atlassian` (Jira/Confluence), `asana`, `linear`, `notion`
* **Design**: `figma`
* **Infrastructure**: `vercel`, `firebase`, `supabase`
* **Communication**: `slack`
* **Monitoring**: `sentry`

### Development workflows

Plugins that add commands and agents for common development tasks:

* **commit-commands**: Git commit workflows including commit, push, and PR creation
* **pr-review-toolkit**: Specialized agents for reviewing pull requests
* **agent-sdk-dev**: Tools for building with the Claude Agent SDK
* **plugin-dev**: Toolkit for creating your own plugins

### Output styles

Customize how Claude responds:

* **explanatory-output-style**: Educational insights about implementation choices
* **learning-output-style**: Interactive learning mode for skill building

## Try it: add the demo marketplace

Anthropic also maintains a [demo plugins marketplace](https://github.com/anthropics/claude-code/tree/main/plugins) (`claude-code-plugins`) with example plugins that show what's possible with the plugin system. Unlike the official marketplace, you need to add this one manually.

<Steps>
  <Step title="Add the marketplace">
    From within Claude Code, run the `plugin marketplace add` command for the `anthropics/claude-code` marketplace:

    ```shell  theme={null}
    /plugin marketplace add anthropics/claude-code
    ```

    This downloads the marketplace catalog and makes its plugins available to you.
  </Step>

  <Step title="Browse available plugins">
    Run `/plugin` to open the plugin manager. This opens a tabbed interface with four tabs you can cycle through using **Tab** (or **Shift+Tab** to go backward):

    * **Discover**: browse available plugins from all your marketplaces
    * **Installed**: view and manage your installed plugins
    * **Marketplaces**: add, remove, or update your added marketplaces
    * **Errors**: view any plugin loading errors

    Go to the **Discover** tab to see plugins from the marketplace you just added.
  </Step>

  <Step title="Install a plugin">
    Select a plugin to view its details, then choose an installation scope:

    * **User scope**: install for yourself across all projects
    * **Project scope**: install for all collaborators on this repository
    * **Local scope**: install for yourself in this repository only

    For example, select **commit-commands** (a plugin that adds git workflow commands) and install it to your user scope.

    You can also install directly from the command line:

    ```shell  theme={null}
    /plugin install commit-commands@anthropics-claude-code
    ```

    See [Configuration scopes](/en/settings#configuration-scopes) to learn more about scopes.
  </Step>

  <Step title="Use your new plugin">
    After installing, the plugin's commands are immediately available. Plugin commands are namespaced by the plugin name, so **commit-commands** provides commands like `/commit-commands:commit`.

    Try it out by making a change to a file and running:

    ```shell  theme={null}
    /commit-commands:commit
    ```

    This stages your changes, generates a commit message, and creates the commit.

    Each plugin works differently. Check the plugin's description in the **Discover** tab or its homepage to learn what commands and capabilities it provides.
  </Step>
</Steps>

The rest of this guide covers all the ways you can add marketplaces, install plugins, and manage your configuration.

## Add marketplaces

Use the `/plugin marketplace add` command to add marketplaces from different sources.

<Tip>
  **Shortcuts**: You can use `/plugin market` instead of `/plugin marketplace`, and `rm` instead of `remove`.
</Tip>

* **GitHub repositories**: `owner/repo` format (for example, `anthropics/claude-code`)
* **Git URLs**: any git repository URL (GitLab, Bitbucket, self-hosted)
* **Local paths**: directories or direct paths to `marketplace.json` files
* **Remote URLs**: direct URLs to hosted `marketplace.json` files

### Add from GitHub

Add a GitHub repository that contains a `.claude-plugin/marketplace.json` file using the `owner/repo` format—where `owner` is the GitHub username or organization and `repo` is the repository name.

For example, `anthropics/claude-code` refers to the `claude-code` repository owned by `anthropics`:

```shell  theme={null}
/plugin marketplace add anthropics/claude-code
```

### Add from other Git hosts

Add any git repository by providing the full URL. This works with any Git host, including GitLab, Bitbucket, and self-hosted servers:

Using HTTPS:

```shell  theme={null}
/plugin marketplace add https://gitlab.com/company/plugins.git
```

Using SSH:

```shell  theme={null}
/plugin marketplace add git@gitlab.com:company/plugins.git
```

To add a specific branch or tag, append `#` followed by the ref:

```shell  theme={null}
/plugin marketplace add https://gitlab.com/company/plugins.git#v1.0.0
```

### Add from local paths

Add a local directory that contains a `.claude-plugin/marketplace.json` file:

```shell  theme={null}
/plugin marketplace add ./my-marketplace
```

You can also add a direct path to a `marketplace.json` file:

```shell  theme={null}
/plugin marketplace add ./path/to/marketplace.json
```

Or add a remote `marketplace.json` file via URL:

```shell  theme={null}
/plugin marketplace add https://example.com/marketplace.json
```

## Install plugins

Once you've added marketplaces, you can install plugins directly (installs to user scope by default):

```shell  theme={null}
/plugin install plugin-name@marketplace-name
```

To choose a different [installation scope](/en/settings#configuration-scopes), use the interactive UI: run `/plugin`, go to the **Discover** tab, and press **Enter** on a plugin. You'll see options for:

* **User scope** (default): install for yourself across all projects
* **Project scope**: install for all collaborators on this repository (adds to `.claude/settings.json`)
* **Local scope**: install for yourself in this repository only (not shared with collaborators)

You may also see plugins with **managed** scope—these are installed by enterprise administrators via [managed settings](/en/settings#enterprise-managed-policy-settings) and cannot be modified.

Run `/plugin` and go to the **Installed** tab to see your plugins grouped by scope.

<Warning>
  Make sure you trust a plugin before installing it. Anthropic does not control what MCP servers, files, or other software are included in plugins and cannot verify that they work as intended. Check each plugin's homepage for more information.
</Warning>

## Manage installed plugins

Run `/plugin` and go to the **Installed** tab to view, enable, disable, or uninstall your plugins.

You can also manage plugins with direct commands.

Disable a plugin without uninstalling:

```shell  theme={null}
/plugin disable plugin-name@marketplace-name
```

Re-enable a disabled plugin:

```shell  theme={null}
/plugin enable plugin-name@marketplace-name
```

Completely remove a plugin:

```shell  theme={null}
/plugin uninstall plugin-name@marketplace-name
```

The `--scope` option lets you target a specific scope with CLI commands:

```shell  theme={null}
claude plugin install formatter@your-org --scope project
claude plugin uninstall formatter@your-org --scope project
```

## Manage marketplaces

You can manage marketplaces through the interactive `/plugin` interface or with CLI commands.

### Use the interactive interface

Run `/plugin` and go to the **Marketplaces** tab to:

* View all your added marketplaces with their sources and status
* Add new marketplaces
* Update marketplace listings to fetch the latest plugins
* Remove marketplaces you no longer need

### Use CLI commands

You can also manage marketplaces with direct commands.

List all configured marketplaces:

```shell  theme={null}
/plugin marketplace list
```

Refresh plugin listings from a marketplace:

```shell  theme={null}
/plugin marketplace update marketplace-name
```

Remove a marketplace:

```shell  theme={null}
/plugin marketplace remove marketplace-name
```

<Warning>
  Removing a marketplace will uninstall any plugins you installed from it.
</Warning>

### Configure auto-updates

Claude Code can automatically update marketplaces and their installed plugins at startup. When auto-update is enabled for a marketplace, Claude Code refreshes the marketplace data and updates installed plugins to their latest versions. If any plugins were updated, you'll see a notification suggesting you restart Claude Code.

Toggle auto-update for individual marketplaces through the UI:

1. Run `/plugin` to open the plugin manager
2. Select **Marketplaces**
3. Choose a marketplace from the list
4. Select **Enable auto-update** or **Disable auto-update**

Official Anthropic marketplaces have auto-update enabled by default. Third-party and local development marketplaces have auto-update disabled by default.

To disable all automatic updates entirely for both Claude Code and all plugins, set the `DISABLE_AUTOUPDATER` environment variable. See [Auto updates](/en/setup#auto-updates) for details.

## Configure team marketplaces

Team admins can set up automatic marketplace installation for projects by adding marketplace configuration to `.claude/settings.json`. When team members trust the repository folder, Claude Code prompts them to install these marketplaces and plugins.

For full configuration options including `extraKnownMarketplaces` and `enabledPlugins`, see [Plugin settings](/en/settings#plugin-settings).

## Troubleshooting

### /plugin command not recognized

If you see "unknown command" or the `/plugin` command doesn't appear:

1. **Check your version**: Run `claude --version`. Plugins require version 1.0.33 or later.
2. **Update Claude Code**:
   * **Homebrew**: `brew upgrade claude-code`
   * **npm**: `npm update -g @anthropic-ai/claude-code`
   * **Native installer**: Re-run the install command from [Setup](/en/setup)
3. **Restart Claude Code**: After updating, restart your terminal and run `claude` again.

### Common issues

* **Marketplace not loading**: Verify the URL is accessible and that `.claude-plugin/marketplace.json` exists at the path
* **Plugin installation failures**: Check that plugin source URLs are accessible and repositories are public (or you have access)
* **Files not found after installation**: Plugins are copied to a cache, so paths referencing files outside the plugin directory won't work
* **Plugin Skills not appearing**: Clear the cache with `rm -rf ~/.claude/plugins/cache`, restart Claude Code, and reinstall the plugin. See [Plugin Skills not appearing](/en/skills#plugin-skills-not-appearing-after-installation) for details.

For detailed troubleshooting with solutions, see [Troubleshooting](/en/plugin-marketplaces#troubleshooting) in the marketplace guide. For debugging tools, see [Debugging and development tools](/en/plugins-reference#debugging-and-development-tools).

## Next steps

* **Build your own plugins**: See [Plugins](/en/plugins) to create custom commands, agents, and hooks
* **Create a marketplace**: See [Create a plugin marketplace](/en/plugin-marketplaces) to distribute plugins to your team or community
* **Technical reference**: See [Plugins reference](/en/plugins-reference) for complete specifications


---

> To find navigation and other pages in this documentation, fetch the llms.txt file at: https://code.claude.com/docs/llms.txt