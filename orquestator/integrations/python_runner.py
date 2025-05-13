import time
import platform
import subprocess
from pathlib import Path

def execute(step: dict) -> dict:
    script_path = Path(step["script"]).resolve()
    if not script_path.is_file():
        return {"error": f"Script not found: {script_path}"}

    venv_dir = Path(step.get("venv", "")).resolve()
    if venv_dir.is_dir():
        if platform.system() == "Windows":
            python_exe = venv_dir / "Scripts" / "python.exe"
        else:
            python_exe = venv_dir / "bin" / "python"
        if not python_exe.is_file():
            return {"error": f"Python binary not found in venv: {python_exe}"}
    else:
        python_exe = Path("python")  # fallback to system Python

    args = step.get("args", [])
    retries = step.get("retries", 5)
    interval = step.get("interval", 5)
    expected_status = step.get("expected_status")  # e.g. "ready", "success", etc.

    last_output = None

    for attempt in range(1, retries + 1):
        try:
            cmd = [str(python_exe), str(script_path), *args]
            proc = subprocess.run(cmd, cwd=str(script_path.parent), capture_output=True, text=True)
            output = proc.stdout.strip()
            last_output = output

            # If you're checking for an exact string or JSON key-value
            if expected_status:
                if expected_status in output:
                    return {
                        "code": 0,
                        "response": output,
                        "attempt": attempt
                    }
            else:
                # No specific check, just return if success
                return {
                    "code": proc.returncode,
                    "response": output,
                    "attempt": attempt
                }
        except Exception as e:
            last_output = str(e)

        if attempt < retries:
            time.sleep(interval)

    return {
        "error": "All retries exhausted",
        "last_response": last_output
    }

