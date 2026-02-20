# Agent Sandboxes

## Quick Start 1: Run prompt from file in sandbox:

This example assumes the plan file is located on the local folder relative to the directory where the command is run.

1. Create a plan using claude in the project folder.
2. Run the following command (replace params as required).
3. **NOTE**: Currently the default timeout is 30 minutes and there is no cli param to override that. Of course, we can update it in `apps/sandbox_workflows/src/prompts/sandbox_fork_agent_system_prompt.md`

```bash
cd apps/sandbox_workflows && uv run obox https://github.com/reanblock/todo-app-with-claude.git \
  --prompt ../../../todo-app-with-claude/specs/agenda-list-view.md \
  --branch feature/agenda-list-view \
  --model sonnet \
  --forks 1
```

While this is runnning you can check status in the [e2b Dashboard](https://e2b.dev/dashboard/darrenjensen/sandboxes?tab=monitoring) or run any of [these cli commands](./apps/sandbox_cli/README.md).

**TIP**: You can try to SSH into the running e2b instance using `cd apps/sandbox_cli && uv run sbx sandbox connect $SANDBOX_ID` (NOTE: this appears to be buggy and may only estabilsih an SSH session **while Claude is actively running** - consider improving later!).

## Quick Start

1. Clone this "agent_sandboxes" repo and cd into it.
2. Run `claude setup-token` to get an OAUTH token to use in the next step.
3. Add `.env` to the project root with the `E2B_API_KEY` and `CLAUDE_CODE_OAUTH_TOKEN` set.
4. Run `cp .env apps/sandbox_agent_working_dir/.env` 
5. Run `cp apps/sandbox_agent_working_dir/.mcp.json.sandbox apps/sandbox_agent_working_dir/.mcp.json` and add the `E2B_API_KEY`.
6. Run the following sanity check command to see its working: `cd apps/sandbox_workflows && uv run obox https://github.com/reanblock/todo-app-with-claude.git --prompt "Install dependencies, start the dev server, and report the public URL. Do nothing else." --max-turns 100 --model haiku`
7. Open two separate claude code instances in yolo mode using sonnet.
8. In the first instance, run `/prime_obox` which makes this the orchestrator.
9. In the second instance use to generate a list of prompt variations you need.
10. In the first instance (orchestrator) run the following prompt: `run obox <github-url>, <new-feature-branch-name>, model: <model-to-use>, forks: <number>, promot: <your-promot>`.
11. Sandbox logs will be saved in `apps/sandbox_agent_working_dir/logs/` directly.
12. Interact with sandbox using cli. README [here](./apps/sandbox_cli/README.md)

**EXAMPLE PROMPT**

In the orchestrator Claude Code window, try the following prompt:

```bash
run obox: https://github.com/reanblock/todo-app-with-claude.git, todo-app-buttons, model: haiku, fork: 1, prompt: Update the style of the Add Chore button to make it animated.
```

The equivalent cli command is the following:

```bash
cd apps/sandbox_workflows && uv run obox https://github.com/reanblock/todo-app-with-claude.git --branch todo-app-buttons --model haiku --prompt "Update the style of the Add Chore button to make it animated." --forks 1
```

## Original README below..

>
> Here we explore e2b agent sandboxes and claude code together to scale your agentic engineering.
>
> Watch the full video where we break down agent sandboxes and claude code [here](https://youtu.be/1ECn5zrVUB4)

Using Agent Sandboxes (E2B) for complete agentic engineering control.

<img src="images/agent_sandboxes_snapshot.png" alt="Agent Sandboxes Architecture Diagram" width="800">

## Value Proposition
> 
> Agent Sandboxes unlock 3 key capabilities for your agentic engineering:

- **Isolation**: Each agent fork runs in a fully isolated, gated E2B sandbox, this means no matter what your agent does, it's secure and safe from your local filesystem and production environment.
- **Scale**: You can run as many agent forks as you want, each fork is independent and has its own sandbox. This is a very literal way to scale your compute to scale your impact.
- **Agency**: Your agents have full control over the sandbox environment, they can install packages, modify files, run commands, etc. This means they can handle more of the engineering process for you.

## Apps

- `sandbox_workflows/` - **obox**: Run parallel agent forks in isolated E2B sandboxes for experimentation
- `sandbox_mcp/` - MCP server wrapping sandbox_cli for LLM integration (works from root)
- `sandbox_cli/` - Click CLI for E2B sandbox management (init, exec, files, lifecycle)
- `sandbox_fundamentals/` - E2B SDK learning examples and patterns
- `cc_in_sandbox/` - Run Claude Code agent inside an E2B sandbox (ibox: in box agent)
- `sandbox_agent_working_dir/` - Agent runtime working directory

## Agent Sandbox Tooling Choice

Using **[e2b](https://e2b.dev/)** (General Sandbox SDK) for:
- Full control over sandbox environment
- Shell command execution
- File system operations
- Running tools (Claude Code, git, npm, etc.)

## Quick Start

### 1. Global Environment Setup

Create a `.env` file in the project root with the following API keys:

```bash
# Required for all sandbox operations
E2B_API_KEY=your_e2b_api_key_here

# Authentication: set ONE of these, not both
# Option 1: API key (pay-per-use billing via Anthropic Console)
ANTHROPIC_API_KEY=your_anthropic_api_key_here
# Option 2: OAuth token (Claude Pro/Max subscription billing)
# Generate with: claude setup-token
CLAUDE_CODE_OAUTH_TOKEN=your_oauth_token_here

# Optional: Required for git push/PR functionality
GITHUB_TOKEN=your_github_token_here
```

> **Note:** Set either `ANTHROPIC_API_KEY` or `CLAUDE_CODE_OAUTH_TOKEN`, not both. The API key uses pay-per-token billing through the Anthropic Console, while the OAuth token bills through your Claude Pro/Max subscription (the same auth method used by `claude-code-action`). If both are set, `ANTHROPIC_API_KEY` takes precedence and a warning is logged.

**Install the top Agentic Coding Tool:**
- **Claude Code**: [https://www.claude.com/product/claude-code](https://www.claude.com/product/claude-code)

**Get your API keys:**
- **E2B API Key**: [https://e2b.dev/docs](https://e2b.dev/docs) - Sign up and get your API key
- **Anthropic API Key**: [https://console.anthropic.com/](https://console.anthropic.com/) - Create an API key in your account settings
- **Claude Code OAuth Token**: Run `claude setup-token` to generate an OAuth token for Claude Pro/Max subscription billing
- **GitHub Token**: [https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens) - Create a personal access token with `repo` scope

### 2. Application Usage

I recommend working from the atoms of the codebase (e2b fundamentals, cli, mcp) to the full e2e sandbox workflow (obox workflows).

**Process:**
1. Setup environment variables
2. Explore E2B Fundamentals `apps/sandbox_fundamentals/`
3. Explore E2B CLI `apps/sandbox_cli/`
4. Explore E2B MCP `apps/sandbox_mcp/`
5. Explore E2B Workflow `apps/sandbox_workflows/`

#### Explore E2B Fundamentals - `apps/sandbox_fundamentals/`

> **Start Here**

Recommended: Walk through all example scripts to understand E2B sandbox concepts.

```bash
cd apps/sandbox_fundamentals
uv sync

# Run through all examples in order
uv run python 01_basic_sandbox.py
uv run python 01_basic_sandbox_keep_alive.py
uv run python 02_list_files.py
uv run python 03_file_operations.py
uv run python 04_run_commands.py
uv run python 05_environment_vars.py
uv run python 06_background_commands.py
uv run python 07_reuse_sandbox.py
uv run python 08_pause_resume.py
uv run python 09_claude_code_agent.py
uv run python 10_install_packages.py
uv run python 11_git_operations.py
uv run python 12_custom_template_build.py
uv run python 12_custom_template_reuse.py
uv run python 13_expose_simple_webserver.py
uv run python 13_expose_vite_vue_webserver.py
```

#### Use CLI for Sandbox Management - `apps/sandbox_cli/`
```bash
cd apps/sandbox_cli
uv sync

# Get help
uv run python src/main.py --help

# Initialize a new sandbox
uv run python src/main.py init

# Create a sandbox with custom template (this is an e2b sandbox template - you can create this by running the `uv run python 12_custom_template_build.py` script)
uv run python src/main.py sandbox create --template agent-sandbox-dev-node22

# Execute a command in a sandbox
uv run python src/main.py exec <sandbox-id> "ls -la"

# List files in a sandbox
uv run python src/main.py files ls <sandbox-id> /
```

You can also boot up a claude code agent and run `/prime_cli_sandbox.md` - then prompt your agent to run the commands for you.

#### Use MCP Server with Claude Desktop - `apps/sandbox_mcp/`
Works from project root - MCP server is configured in your Claude Desktop config.
```bash
# cp the .mcp.json.sandbox to .mcp.json
cp .mcp.json.sandbox .mcp.json

# replace your e2b api key in the .mcp.json env section
...

# Start a claude code agent with the .mcp.json
claude

# Check the mcp server status
/mcp

# Prompt the same commands as you would with the sandbox_cli with natural language
prompt: What can we do with the e2b sandbox tools?

prompt: init a new sandbox

prompt: create a sandbox with custom template agent-sandbox-dev-node22

prompt: run ls -la in the sandbox

prompt: search for all .py files in the sandbox with exec

# Run custom slash commands
prompt: /plan Add buttons to the nav bar that auto scroll to respective sections on the landing page

prompt: /build <path-to-plan>

prompt: /wf_plan_build Add buttons to the nav bar that auto scroll to respective sections on the landing page

```

#### Run Parallel Agent Experiments - **obox** - `apps/sandbox_workflows/`
```bash
cp .mcp.json apps/sandbox_agent_working_dir/.mcp.json (after you fill it out with your e2b api key)
cp .env apps/sandbox_agent_working_dir/.env (after you fill it out with your credentials)

cd apps/sandbox_workflows
uv sync
uv run obox <repo-url> --branch <branch> --model <opus|sonnet|haiku> --prompt "your task" --forks 3
```

You can also boot up a claude code agent and run `/prime_obox.md` - then prompt your agent to run the commands for you.

See `apps/*/README.md` for detailed documentation on each tool.

## Application Notes

### obox - `apps/sandbox_workflows/`

- There are two system prompts for the custom agent that drives the sandbox engineering
  - `apps/sandbox_workflows/src/prompts/sandbox_fork_agent_w_github_token_system_prompt.md` - Supports GitHub token auth for git push/PR functionality
  - `apps/sandbox_workflows/src/prompts/sandbox_fork_agent_system_prompt.md` - Basic system prompt for sandbox engineering, does not have git push/PR functionality
  - You can either use specific prompt workflows (see `apps/sandbox_agent_working_dir/.claude/commands/wf_plan_build.md`) to manage git operations, or you can use the system prompt.
- The agents working directory is `apps/sandbox_agent_working_dir/` see `apps/sandbox_workflows/src/modules/constants.py` for more details.
  - That means that `apps/sandbox_agent_working_dir/./claude/commands/` are the available slash commands for the agent (and all the other claude capabilities are active there too)

## Resources

- https://e2b.dev/
- https://www.claude.com/product/claude-code
- https://docs.claude.com/en/docs/agent-sdk/python
- See `ai_docs/README.md` for resources used to build this codebase.

## Master **Agentic Coding**
> Prepare for the future of software engineering

Learn tactical agentic coding patterns with [Tactical Agentic Coding](https://agenticengineer.com/tactical-agentic-coding?y=agsbx)

Follow the [IndyDevDan YouTube channel](https://www.youtube.com/@indydevdan) to improve your agentic coding advantage.

