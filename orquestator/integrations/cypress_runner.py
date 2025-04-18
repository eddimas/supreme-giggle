# integrations/cypress_runner.py

import subprocess
import platform
import os
from pathlib import Path
from app import CYPRESS_MODULES

def execute(step: dict) -> dict:
    project = Path(step.get("project", ".")).resolve()
    if not project.is_dir():
        return {"error": f"Project folder not found: {project}"}

    # resolve folder vs module
    folder = step.get("folder")
    if step.get("module"):
        folder = CYPRESS_MODULES.get(step["module"], folder)
    if not folder:
        return {"error": "Must specify 'folder' or 'module'"}

    spec_dir = project / folder
    if not spec_dir.exists():
        return {"error": f"Spec folder not found: {spec_dir}"}

    # glob both *.cy.js and *.spec.js
    patterns = [str(spec_dir / "**" / "*.cy.js"), str(spec_dir / "**" / "*.spec.js")]
    spec_pattern = ",".join(patterns)

    # pick the binary
    system = platform.system()
    if system == "Windows":
        local_cypress = project / "node_modules" / ".bin" / "cypress.cmd"
    else:
        local_cypress = project / "node_modules" / ".bin" / "cypress"

    if local_cypress.exists():
        runner = str(local_cypress)
        # when using the binary directly, you DO need the "run" subcommand
        cmd = [runner, "run", "--spec", spec_pattern,
               "--reporter", "spec", "--no-color"]
    else:
        # fallback to npx
        if system == "Windows":
            local_npx = project / "node_modules" / ".bin" / "npx.cmd"
        else:
            local_npx = project / "node_modules" / ".bin" / "npx"
        npx_cmd = str(local_npx) if local_npx.exists() else "npx"
        cmd = [npx_cmd, "cypress", "run", "--spec", spec_pattern,
               "--reporter", "spec", "--no-color"]

    # build a clean env (we’re no longer loading system proxies)
    env = os.environ.copy()
    # strip any lingering color-related env vars if you want
    env.pop("FORCE_COLOR", None)

    try:
        proc = subprocess.run(
            cmd,
            cwd=str(project),
            env=env,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
    except FileNotFoundError as e:
        return {"error": f"Executable not found: {cmd[0]}", "exception": str(e)}

    return {
        "out":  proc.stdout,   # full spec‑style output in plain text
        "err":  proc.stderr,   # should now just be warnings, not decode errors
        "code": proc.returncode
    }
