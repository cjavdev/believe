---
name: fix-render-deploy
description: Diagnose and fix failing Render deployments for the current project. Fetches deployment logs, identifies the root cause of failures, and creates a PR with the fix.
---

# Fix Render Deployment

Diagnose and fix failing Render deployments for the current project by analyzing logs and creating a pull request with the fix.

## Workflow

### Step 1: Configure Render Workspace and Service

**IMPORTANT:** Always start by configuring the Render MCP server with the correct workspace and service for this project.

1. Select the workspace using `mcp__render__select_workspace` with:
   - `ownerID`: `tea-cspsoo0gph6c73f47r5g`

2. Use the service ID for this project:
   - `serviceId`: `srv-d5qk7dv5r7bs738mlolg`

This project's Render service is pre-configured, so skip any service discovery steps.

### Step 2: Check Recent Deployments

1. Use `mcp__render__list_deploys` with `serviceId`: `srv-d5qk7dv5r7bs738mlolg` to get recent deployments
2. Find the most recent failed deployment - look for:
   - `status: "build_failed"` - build-time failure
   - `status: "deploy_failed"` - runtime/startup failure
   - `status: "update_failed"` - configuration update failure
3. Note the deploy ID and failure type for fetching appropriate logs

### Step 3: Fetch and Analyze Logs

1. Use `mcp__render__list_logs` with:
   - `resource`: `["srv-d5qk7dv5r7bs738mlolg"]`
   - `type`: Choose based on failure type:
     - `["build"]` for build failures
     - `["app"]` for runtime/startup failures
   - `limit`: 100 (to get enough context)

2. Analyze the logs to identify the root cause. Common failure patterns:

   **Dependency Issues:**
   - `ModuleNotFoundError: No module named 'xyz'` → Add to requirements.txt
   - `ImportError: cannot import name 'X' from 'Y'` → Version mismatch or missing extra
   - `ERROR: Could not find a version that satisfies the requirement` → Invalid package name or version

   **Build Failures:**
   - `SyntaxError` → Python syntax error in code
   - `error: command 'gcc' failed` → Missing system dependency
   - `npm ERR! code ERESOLVE` → Dependency resolution conflict

   **Runtime Failures:**
   - `bind: address already in use` → Wrong port configuration
   - `Error: connect ECONNREFUSED` → Database/service not accessible
   - `TimeoutError` → Slow startup, increase health check timeout

### Step 4: Implement the Fix

1. Based on the log analysis, identify the file(s) that need to be modified
2. Read the relevant files to understand the current state
3. Make the necessary code changes to fix the issue
4. Common fixes:
   - Add missing packages to `requirements.txt` or `package.json`
   - Fix import statements
   - Update configuration files (render.yaml, runtime.txt)
   - Fix environment variable references

### Step 5: Create a Pull Request

1. Create a new branch with a descriptive name:
   ```bash
   git checkout -b fix/render-deploy-<short-description>
   ```

2. Stage and commit the changes:
   ```bash
   git add <files>
   git commit -m "Fix: <description of the fix>"
   ```

3. Push the branch:
   ```bash
   git push -u origin fix/render-deploy-<short-description>
   ```

4. Use `mcp__github-official__create_pull_request` to create a PR with:
   - `owner`: Repository owner from git remote
   - `repo`: Repository name from git remote
   - `title`: Clear title like "Fix Render deployment: <issue summary>"
   - `head`: The branch you created
   - `base`: `main` (or the default branch)
   - `body`: Include:
     - **Summary**: Brief description of the deployment failure
     - **Root Cause**: What was identified from the logs
     - **Fix**: Description of the changes made
     - **Testing**: Any local testing performed

## Example PR Body

```markdown
## Summary
Fix failing Render deployment caused by missing dependency.

## Root Cause
Build logs showed:
```
ModuleNotFoundError: No module named 'email_validator'
```

The `pydantic[email]` extra was not installed, which is required for email validation in Pydantic models.

## Fix
Added `pydantic[email]` to requirements.txt to include the email-validator dependency.

## Testing
- Verified locally with `pip install -r requirements.txt`
- Confirmed `from pydantic import EmailStr` works correctly
```

## Notes

- Always verify the fix locally before creating the PR if possible
- If the issue is environment-specific (env vars, secrets), note this in the PR and don't commit sensitive values
- If multiple issues are found, prioritize the first failure in the build/deploy process
