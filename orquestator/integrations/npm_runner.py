# integrations/npm_runner.py

import subprocess
import platform
import shutil
import os
from pathlib import Path
from dotenv import load_dotenv
from datetime import datetime  # ← new import

def execute(step: dict) -> dict:
    """
    Runs an `npm run <script>` command in its own Node project,
    returning stdout, stderr, exit code, plus timestamps and duration.
    """
    # 1) Locate & validate the project folder
    project = Path(step.get("project", ".")).resolve()
    if not project.is_dir():
        return {"error": f"Project folder not found: {project}"}

    # 2) Load .env if present
    dotenv_path = project / ".env"
    if dotenv_path.is_file():
        load_dotenv(dotenv_path, override=True)

    # 3) Find npm binary
    npm_cmd = "npm.cmd" if platform.system() == "Windows" else "npm"
    npm_path = shutil.which(npm_cmd)
    if not npm_path:
        return {"error": f"npm executable not found in PATH (looked for {npm_cmd})"}

    # 4) Ensure deps are installed
    install = subprocess.run(
        [npm_path, "install"],
        cwd=str(project),
        capture_output=True,
        text=True
    )
    if install.returncode != 0:
        return {
            "error": "npm install failed",
            "out": install.stdout,
            "err": install.stderr
        }

    # 5) Build env
    env = os.environ.copy()
    bin_dir = project / "node_modules" / ".bin"
    env["PATH"] = str(bin_dir) + os.pathsep + env.get("PATH", "")
    for k, v in step.get("env", {}).items():
        env[k] = v

    # 6) Determine which script to run
    script = step.get("script")
    if not script:
        return {"error": "No `script` specified for npm step"}

    cmd = [npm_path, "run", script] + step.get("args", [])

    # 7) Execute and measure time
    start_time = datetime.now()              # ← record start
    try:
        proc = subprocess.run(
            cmd,
            cwd=str(project),
            env=env,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace"
        )
        end_time = datetime.now()            # ← record end
        duration = (end_time - start_time).total_seconds()
        return {
            "out":      proc.stdout,
            "err":      proc.stderr,
            "code":     proc.returncode,
            "start":    start_time.isoformat(),
            "end":      end_time.isoformat(),
            "duration": duration
        }
    except FileNotFoundError as e:
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        return {
            "error":     f"Executable not found: {cmd[0]}",
            "exception": str(e),
            "start":     start_time.isoformat(),
            "end":       end_time.isoformat(),
            "duration":  duration
        }