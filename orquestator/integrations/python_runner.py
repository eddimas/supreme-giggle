import subprocess
import platform
from pathlib import Path

def execute(step: dict) -> dict:
    """
    Runs a Python script inside its own virtualenv.

    Expects step to have:
      - script: path to the .py file
      - venv:    path to the venv root (with Scripts/ or bin/)
      - args:    optional list of args
    """
    script_path = Path(step["script"]).resolve()
    if not script_path.is_file():
        return {"error": f"Script not found: {script_path}"}

    # pick the right venv python exe on Windows vs Linux/Mac
    venv_dir = Path(step.get("venv", "")).resolve()
    if venv_dir.is_dir():
        if platform.system() == "Windows":
            python_exe = venv_dir / "Scripts" / "python.exe"
        else:
            python_exe = venv_dir / "bin" / "python"
        if not python_exe.is_file():
            return {"error": f"Python binary not found in venv: {python_exe}"}
    else:
        # no venv provided or missing: fall back to system python
        python_exe = Path("python")

    cmd = [str(python_exe), str(script_path), *step.get("args", [])]
    cwd = script_path.parent

    proc = subprocess.run(cmd, cwd=str(cwd), capture_output=True, text=True)
    return {
        "out":  proc.stdout,
        "err":  proc.stderr,
        "code": proc.returncode
    }
