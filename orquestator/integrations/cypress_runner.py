# integrations/cypress_runner.py

import subprocess
import platform
from pathlib import Path
from app import CYPRESS_MODULES

def execute(step: dict) -> dict:
    project = Path(step.get("project", ".")).resolve()
    if not project.is_dir():
        return {"error": f"Project folder not found: {project}"}

    # figure out test folder
    folder = step.get("folder")
    if step.get("module"):
        folder = CYPRESS_MODULES.get(step["module"], folder)
    if not folder:
        return {"error": "Must specify 'folder' or 'module'"}

    spec_dir = project / folder
    if not spec_dir.exists():
        return {"error": f"Spec folder not found: {spec_dir}"}

    # glob both *.cy.js and *.spec.js under that folder
    patterns = [str(spec_dir / "**" / "*.cy.js"), str(spec_dir / "**" / "*.spec.js")]
    spec_pattern = ",".join(patterns)

    # 1) Try the local binary
    if platform.system() == "Windows":
        local_bin = project / "node_modules" / ".bin" / "cypress.cmd"
    else:
        local_bin = project / "node_modules" / ".bin" / "cypress"

    if local_bin.exists():
        cmd = [str(local_bin), "run", "--spec", spec_pattern]

    else:
        # 2) Try a local npx in the project
        if platform.system() == "Windows":
            local_npx = project / "node_modules" / ".bin" / "npx.cmd"
        else:
            local_npx = project / "node_modules" / ".bin" / "npx"

        if local_npx.exists():
            npx_cmd = str(local_npx)
        else:
            # 3) Fallback to global npx
            npx_cmd = "npx"

        # final check: if npx_cmd isn't on disk and not on PATH, we'll catch below
        cmd = [npx_cmd, "cypress", "run", "--spec", spec_pattern]

    try:
        proc = subprocess.run(
            cmd,
            cwd=str(project),
            capture_output=True,
            text=True
        )
    except FileNotFoundError as e:
        # Clearly report which executable wasn't found
        return {"error": f"Executable not found: {cmd[0]}", "exception": str(e)}

    return {
        "out":  proc.stdout,
        "err":  proc.stderr,
        "code": proc.returncode
    }
