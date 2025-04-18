# integrations/python_runner.py

import subprocess
from pathlib import Path

def execute(step: dict) -> dict:
    """
    Runs a Python script inside its own virtualenv.
    Expects step to have:
      - script: path to the .py file
      - venv:    path to the venv root (contains bin/python)
      - args:    optional list of args
    """
    # Resolve script and venv dirs absolutely
    script_path = Path(step["script"]).resolve()
    venv_dir    = Path(step.get("venv", "")).resolve()

    if not script_path.is_file():
        return {"error": f"Script not found: {script_path}"}

    # Point at the real python inside the venv
    python_exe = venv_dir / "bin" / "python"
    if not python_exe.is_file():
        return {"error": f"Python binary not found at {python_exe}"}

    # Build the command with the absolute python
    cmd = [str(python_exe), str(script_path), *step.get("args", [])]

    # Run with cwd set to the script's folder (for relative imports/configs)
    cwd = script_path.parent

    proc = subprocess.run(
        cmd,
        cwd=str(cwd),
        capture_output=True,
        text=True
    )

    return {
        "out":  proc.stdout,
        "err":  proc.stderr,
        "code": proc.returncode
    }
