import subprocess
import platform
import os
from pathlib import Path
from dotenv import load_dotenv
from app import CYPRESS_MODULES

def execute(step: dict) -> dict:
    """
    1) Loads .env from the project root (overrides nothing else).
    2) Picks the right cypress binary (local .cmd on Windows, or npx fallback).
    3) Runs with that env dict, so http_proxy/https_proxy from .env are honored.
    """
    project = Path(step.get("project", ".")).resolve()
    if not project.is_dir():
        return {"error": f"Project folder not found: {project!s}"}

    # 1. Load .env
    dotenv_path = project / ".env"
    if dotenv_path.is_file():
        load_dotenv(dotenv_path, override=True)

    # 2. Build the filtered env dict
    #    We drop any system proxy vars, then let python-dotenv values stand.
    env = {k: v for k, v in os.environ.items()
           if not k.lower().endswith("_proxy")}
    
    # 3. Resolve folder vs module
    folder = step.get("folder")
    if step.get("module"):
        folder = CYPRESS_MODULES.get(step["module"], folder)
    if not folder:
        return {"error": "Must specify 'folder' or 'module'"}

    spec_dir = project / folder
    if not spec_dir.exists():
        return {"error": f"Spec folder not found: {spec_dir!s}"}

    patterns = [
        str(spec_dir / "**" / "*.cy.js"),
        str(spec_dir / "**" / "*.spec.js")
    ]
    spec_pattern = ",".join(patterns)

    # 4. Find the binary or fall back to npx
    system = platform.system()
    if system == "Windows":
        local_bin = project / "node_modules" / ".bin" / "cypress.cmd"
    else:
        local_bin = project / "node_modules" / ".bin" / "cypress"

    if local_bin.exists():
        runner = str(local_bin)
        cmd = [runner, "run", "--spec", spec_pattern]
    else:
        # try local npx or global
        if system == "Windows":
            local_npx = project / "node_modules" / ".bin" / "npx.cmd"
        else:
            local_npx = project / "node_modules" / ".bin" / "npx"
        npx_cmd = str(local_npx) if local_npx.exists() else "npx"
        cmd = [npx_cmd, "cypress", "run", "--spec", spec_pattern]

    # 5. Launch!
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
        "out":  proc.stdout,
        "err":  proc.stderr,
        "code": proc.returncode
    }
