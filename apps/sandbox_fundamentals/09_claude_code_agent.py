#!/usr/bin/env -S uv run
# /// script
# dependencies = [
#   "e2b",
#   "python-dotenv",
# ]
# ///

"""
Setup Claude Code agent in sandbox, sync version with local, run prompt.
"""

import subprocess
import os
from pathlib import Path
from dotenv import load_dotenv
from e2b import Sandbox
from e2b.sandbox.commands.command_handle import CommandExitException

# Load .env from project root
root_dir = Path(__file__).parent.parent.parent
load_dotenv(root_dir / ".env")

print("=== Claude Code Agent Setup ===\n")

# Get local Claude Code version
print("📍 Checking local Claude Code version...")
local_version = subprocess.run(
    ["claude", "--version"],
    capture_output=True,
    text=True
).stdout.strip().split()[0]
print(f"   Local version: {local_version}")

# Build auth environment variables (set ONE, not both)
auth_envs = {}
anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
claude_code_oauth_token = os.getenv("CLAUDE_CODE_OAUTH_TOKEN")

if anthropic_api_key:
    print("🔑 Found ANTHROPIC_API_KEY in .env")
    auth_envs["ANTHROPIC_API_KEY"] = anthropic_api_key
if claude_code_oauth_token:
    print("🔑 Found CLAUDE_CODE_OAUTH_TOKEN in .env")
    auth_envs["CLAUDE_CODE_OAUTH_TOKEN"] = claude_code_oauth_token

if anthropic_api_key and claude_code_oauth_token:
    print("⚠️  Both ANTHROPIC_API_KEY and CLAUDE_CODE_OAUTH_TOKEN are set. "
          "ANTHROPIC_API_KEY takes precedence. Remove one to avoid conflicts.")
elif not anthropic_api_key and not claude_code_oauth_token:
    print("❌ No authentication configured. Set ANTHROPIC_API_KEY or CLAUDE_CODE_OAUTH_TOKEN in .env")
    exit(1)
else:
    auth_method = "ANTHROPIC_API_KEY" if anthropic_api_key else "CLAUDE_CODE_OAUTH_TOKEN"
    print(f"🔑 Using {auth_method} for authentication")

# Create sandbox with Claude Code template
print("\n🚀 Creating sandbox with Claude Code template...")
sbx = Sandbox.create(
    template='claude-code',
    envs=auth_envs,
    timeout=60 * 5
)
print(f"   Sandbox: {sbx.sandbox_id}")

# Check Claude Code version in sandbox
print("\n🔍 Checking Claude Code in sandbox...")
result = sbx.commands.run("claude --version")
sandbox_version = result.stdout.strip().split()[0]
print(f"   Sandbox version: {sandbox_version}")

# Update if versions don't match
if sandbox_version != local_version:
    print(f"\n⚡ Version mismatch! Updating {sandbox_version} → {local_version}")
    update_result = sbx.commands.run("claude update", timeout=120)
    print(update_result.stdout)

    # Verify update
    result = sbx.commands.run("claude --version")
    new_version = result.stdout.strip().split()[0]
    print(f"   Updated to: {new_version}")
else:
    print("   ✅ Version matches local installation")

# Verify auth env vars are visible in the sandbox
print("\n🔍 Verifying auth env vars in sandbox...")
check = sbx.commands.run(
    "env | grep -E 'ANTHROPIC_API_KEY|CLAUDE_CODE_OAUTH_TOKEN' | sed 's/=.*/=<set>/'",
    envs=auth_envs,
)
if check.stdout.strip():
    print(f"   {check.stdout.strip()}")
else:
    print("   ⚠️  No auth env vars found in sandbox environment!")

# Remove apiKeyHelper from sandbox settings if present (conflicts with CLAUDE_CODE_OAUTH_TOKEN)
print("\n🔧 Checking for apiKeyHelper conflicts in sandbox...")
find_result = sbx.commands.run(
    "grep -rl 'apiKeyHelper' /home/user/.claude/ /etc/ 2>/dev/null || true",
    envs=auth_envs,
)
if find_result.stdout.strip():
    for settings_file in find_result.stdout.strip().split("\n"):
        print(f"   Found apiKeyHelper in: {settings_file}")
        sbx.commands.run(
            f"cat {settings_file}",
            envs=auth_envs,
        )
        # Remove the apiKeyHelper key from the JSON settings file
        sbx.commands.run(
            f"""python3 -c "
import json, sys
with open('{settings_file}', 'r') as f:
    data = json.load(f)
if 'apiKeyHelper' in data:
    del data['apiKeyHelper']
    with open('{settings_file}', 'w') as f:
        json.dump(data, f, indent=2)
    print('   Removed apiKeyHelper from {settings_file}')
else:
    print('   Key not in top-level JSON, skipping')
"
""",
            envs=auth_envs,
        )
else:
    print("   No apiKeyHelper conflicts found")

# Check auth status inside the sandbox
print("\n🔍 Checking claude auth status in sandbox...")
try:
    auth_check = sbx.commands.run("claude auth status 2>&1", envs=auth_envs)
    print(f"   {auth_check.stdout.strip()}")
except CommandExitException as e:
    print(f"   Auth status (exit {e.exit_code}): {e.stdout or e.stderr or 'no output'}")

# Run a simple ping prompt
print("\n🤖 Running Claude Code prompt...")
print("   Prompt: 'Create a simple hello.txt file with a greeting'\n")

try:
    result = sbx.commands.run(
        "echo 'Create a simple hello.txt file with a greeting' | claude -p --dangerously-skip-permissions 2>&1",
        envs=auth_envs,
        timeout=0
    )
    print("📄 Claude Code response:")
    print(result.stdout)
except CommandExitException as e:
    print(f"❌ Claude Code exited with code {e.exit_code}")
    if e.stderr:
        print(f"   stderr: {e.stderr}")
    if e.stdout:
        print(f"   stdout: {e.stdout}")
    sbx.kill()
    exit(1)

# Verify the file was created
print("\n✅ Verifying output...")
if sbx.files.exists("/home/user/hello.txt"):
    content = sbx.files.read("/home/user/hello.txt")
    print(f"   ✓ File created: /home/user/hello.txt")
    print(f"   Content: {content.strip()}")
else:
    print("   ✗ File not found")

# List files created
files = sbx.files.list("/home/user")
print(f"\n📁 Total files in /home/user: {len(files)}")

# Clean up
sbx.kill()
print("\n🛑 Sandbox killed")
