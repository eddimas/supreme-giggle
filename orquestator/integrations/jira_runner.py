import subprocess
import json

def execute(step: dict) -> dict:
    data = json.dumps({"body": step["comment"]})
    cmd = [
      "curl", "-X", "POST",
      "-u", f"{step['user']}:{step['token']}",
      "-H", "Content-Type: application/json",
      f"{step['jira_url']}/issue/{step['issue']}/comment",
      "--data", data
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    return {
        "out": proc.stdout,
        "err": proc.stderr,
        "code": proc.returncode
    }
