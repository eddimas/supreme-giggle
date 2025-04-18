# integrations/cypress_runner.py

import subprocess
from pathlib import Path
from app import CYPRESS_MODULES

def execute(step: dict) -> dict:
    """
    Runs Cypress tests in a self‑contained project folder.

    Expects step to have:
      - project: path to the node project root (contains package.json + node_modules)
      - folder:  path _inside_ that project where .cy.js specs live
      - (optional) module: a key into CYPRESS_MODULES instead of 'folder'
    """
    project = Path(step.get("project", ".")).resolve()
    if not project.is_dir():
        return {"error": f"Project folder not found: {project!s}"}

    # resolve folder vs module shortcut
    folder = step.get("folder")
    if step.get("module"):
        folder = CYPRESS_MODULES.get(step["module"], folder)
    if not folder:
        return {"error": "No 'folder' or 'module' specified in step"}

    spec_dir = project / folder
    if not spec_dir.exists():
        return {"error": f"Spec folder not found: {spec_dir!s}"}

    patterns = [
        str(spec_dir / "**" / "*.cy.js"),
        str(spec_dir / "**" / "*.spec.js")
    ]
    spec_pattern = ",".join(patterns)

    # prefer the locally installed binary
    local_bin = project / "node_modules" / ".bin" / "cypress"
    if local_bin.exists():
        # __directly__ call the binary with "run"
        cmd = [str(local_bin), "run", "--spec", spec_pattern]
    else:
        # fallback to npx
        cmd = ["npx", "cypress", "run", "--spec", spec_pattern]

    proc = subprocess.run(
        cmd,
        cwd=str(project),
        capture_output=True,
        text=True
    )

    return {
        "out":  proc.stdout,
        "err":  proc.stderr,
        "code": proc.returncode
    }
