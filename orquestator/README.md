# Orchestrator Workflow API

This project provides a lightweight, file-based Python orchestrator that runs sequential steps—Python scripts, Cypress test suites, Jira updates—without external dependencies like Docker, Redis, or Postgres. All state is persisted in JSON files.

## Prerequisites

1. **Python 3.8+** installed and available on your PATH
2. **Node.js (v14+) & npm** installed for Cypress projects
3. **npm packages** (per-project):
   - `cypress` (installed in each Cypress project's `node_modules`)
4. **curl** (or similar) for Jira integration, or adjust `integrations/jira_runner.py` to use HTTP libraries

## Installation

1. **Clone repository**:

   ```bash
   git clone <repo-url> orchestrator
   cd orchestrator
   ```

2. **Create a virtualenv for the orchestrator** (optional but recommended):

   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```

3. **Install Python deps**:

   ```bash
   pip install -r requirements.txt
   ```

4. **Set up Cypress project(s)**: For each Cypress suite (e.g. `scripts/node/cypress/project1`):

   ```bash
   cd scripts/node/cypress/project1
   npm init -y
   npm install cypress --save-dev
   ```

   Place your tests under `cypress/e2e/` (e.g. `*.cy.js`).

5. **Prepare Python script projects**: For each Python step (e.g. `scripts/python/process1`):

   ```bash
   cd scripts/python/process1
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt  # your script deps
   ```

## Project Structure

```
orchestrator/
├── app.py                # FastAPI app + orchestrator logic
├── persistence.py        # File-based state persistence
├── integrations/         # Step plugins: python_runner, cypress_runner, jira_runner
├── workflows/            # JSON workflow definitions (e.g. deploy.json)
├── runs/                 # Auto-generated run state files
├── requirements.txt      # FastAPI & uvicorn
└── scripts/              # Your project scripts
    ├── python/           # Python script projects with their own .venv
    └── node/             # Node/Cypress projects
```

## Configuration

- **Workflows** live in `workflows/<name>.json`. Define ordered `steps` with keys:

  - `type`: `python` | `cypress` | `jira`
  - Python steps: `script`, `venv` (path to `.venv`), `args` (optional)
  - Cypress steps: `project` (root folder), `folder` (inside project for specs)
  - Jira steps: `jira_url`, `user`, `token`, `issue`, `comment`

- **CYPRESS_MODULES** in `app.py` lets you map short names to folders.

## Running the API

1. **Start server** (from project root):

   ```bash
   uvicorn app:app --reload
   ```

2. **Trigger a workflow**:

   ```bash
   curl -X POST "http://localhost:8000/start?name=deploy"
   # Returns { "run_id": "<uuid>" }
   ```

3. **Check status**:

   ```bash
   curl "http://localhost:8000/status/<run_id>"
   ```

   Response shows `current`, `status` (`pending`|`running`|`failed`|`completed`), and `log` entries per step.

## Defining Workflows

Example `workflows/deploy.json`:

```json
{
  "name": "deploy",
  "steps": [
    {
      "name": "unit tests",
      "type": "python",
      "script": "scripts/python/process1/main.py",
      "venv": "scripts/python/process1/.venv"
    },
    {
      "name": "ui smoke tests",
      "type": "cypress",
      "project": "scripts/node/cypress/project1",
      "folder": "cypress/e2e"
    },
    {
      "name": "notify jira",
      "type": "jira",
      "jira_url": "https://your-jira.cloud.atlassian.net/rest/api/2",
      "user": "jira-user@example.com",
      "token": "YOUR_API_TOKEN",
      "issue": "PROJ-123",
      "comment": "✅ Deployment complete, all tests passed"
    }
  ]
}
```

## Customization

- **Add new integrations**: Drop `integrations/<type>_runner.py` with an `execute(step)` function.
- **Adjust paths**: Modify `CYPRESS_MODULES` or step definitions for different folder layouts.
- **Error handling & retries**: Enhance runners to implement retries or notifications on failures.

---

_For more details or troubleshooting, see code comments in **``** and **``**._
