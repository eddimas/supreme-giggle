import subprocess
import platform
from pathlib import Path
from app import CYPRESS_MODULES

def execute(step: dict) -> dict:
    """
    Runs Cypress tests in a self‑contained project folder.

    Expects step to have:
      - project: path to your node project root
      - folder:  where your .cy.js/.spec.js files live under that project
      - (optional) module: a key into CYPRESS_MODULES instead of folder
    """
    project = Path(step.get("project", ".")).resolve()
    if not project.is_dir():
        return {"error": f"Project folder not found: {project}"}

    # resolve folder vs module shortcut
    folder = step.get("folder")
    if step.get("module"):
        folder = CYPRESS_MODULES.get(step["module"], folder)
    if not folder:
        return {"error": "Must specify 'folder' or 'module' in step"}

    spec_dir = project / folder
    if not spec_dir.exists():
        return {"error": f"Spec folder not found: {spec_dir}"}

    # build glob: both *.cy.js and *.spec.js
    patterns = [
        str(spec_dir / "**" / "*.cy.js"),
        str(spec_dir / "**" / "*.spec.js")
    ]
    spec_pattern = ",".join(patterns)

    # On Windows, just use npx so you get the .cmd shim
    if platform.system() == "Windows":
        cmd = ["npx", "cypress", "run", "--spec", spec_pattern]
    else:
        # POSIX: prefer the local binary if it exists
        local_bin = project / "node_modules" / ".bin" / "cypress"
        if local_bin.exists():
            cmd = [str(local_bin), "run", "--spec", spec_pattern]
        else:
            cmd = ["npx", "cypress", "run", "--spec", spec_pattern]

    proc = subprocess.run(cmd, cwd=str(project), capture_output=True, text=True)
    return {
        "out":  proc.stdout,
        "err":  proc.stderr,
        "code": proc.returncode
    }
