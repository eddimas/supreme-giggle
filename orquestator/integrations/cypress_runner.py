# integrations/cypress_runner.py

import subprocess
import platform
import os
from pathlib import Path
from app import CYPRESS_MODULES

def _load_dotenv(env_path: Path) -> dict:
    """
    Simple .env loader: parses KEY=VAL lines, ignores comments/blanks.
    """
    vars = {}
    for line in env_path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, val = line.split("=", 1)
        vars[key.strip()] = val.strip()
    return vars

def execute(step: dict) -> dict:
    # 1) locate project and spec folder
    project = Path(step.get("project", ".")).resolve()
    if not project.is_dir():
        return {"error": f"Project folder not found: {project}"}

    folder = step.get("folder")
    if step.get("module"):
        folder = CYPRESS_MODULES.get(step["module"], folder)
    if not folder:
        return {"error": "Must specify 'folder' or 'module'"}

    spec_dir = project / folder
    if not spec_dir.exists():
        return {"error": f"Spec folder not found: {spec_dir}"}

    # build glob for both *.cy.js and *.spec.js
    patterns = [
        str(spec_dir / "**" / "*.cy.js"),
        str(spec_dir / "**" / "*.spec.js")
    ]
    spec_pattern = ",".join(patterns)

    # 2) pick the right cypress runner
    system = platform.system()
    if system == "Windows":
        local_cypress = project / "node_modules" / ".bin" / "cypress.cmd"
    else:
        local_cypress = project / "node_modules" / ".bin" / "cypress"

    if local_cypress.exists():
        cmd = [str(local_cypress), "run", "--spec", spec_pattern]
    else:
        # fallback to npx (local or global)
        if system == "Windows":
            local_npx = project / "node_modules" / ".bin" / "npx.cmd"
        else:
            local_npx = project / "node_modules" / ".bin" / "npx"

        npx_cmd = str(local_npx) if local_npx.exists() else "npx"
        cmd = [npx_cmd, "cypress", "run", "--spec", spec_pattern]

    # 3) build a clean env, loading only from .env
    env = os.environ.copy()
    # strip any system proxy vars
    for k in ("http_proxy","https_proxy","HTTP_PROXY","HTTPS_PROXY"):
        env.pop(k, None)

    dotenv_path = project / ".env"
    if dotenv_path.is_file():
        file_vars = _load_dotenv(dotenv_path)
        # only inject proxy keys found in the file
        for key, val in file_vars.items():
            if key.lower() in ("http_proxy","https_proxy"):
                env[key] = val

    # 4) run in the project folder
    try:
        proc = subprocess.run(
            cmd,
            cwd=str(project),
            env=env,
            capture_output=True,
            text=True
        )
    except FileNotFoundError as e:
        return {"error": f"Executable not found: {cmd[0]}", "exception": str(e)}

    return {
        "out":  proc.stdout,
        "err":  proc.stderr,
        "code": proc.returncode
    }
