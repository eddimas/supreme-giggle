# integrations/api_runner.py

import time
import requests
from pathlib import Path

def execute(step: dict) -> dict:
    """
    Polls a long‑running API until a desired status appears (or retries exhaust).

    Workflow step keys:
      - url            (str): endpoint to call
      - method         (str, default="GET")
      - headers        (dict, optional)
      - body           (dict, optional)
      - status_field   (str, optional): JSON field to inspect
      - desired_status (any, optional): value of status_field we wait for
      - retries        (int, default=10): max attempts
      - interval       (int, default=5): seconds between attempts
    """
    url    = step["url"]
    method = step.get("method", "GET").upper()
    headers= step.get("headers", {})
    body   = step.get("body")
    retries = step.get("retries", 10)
    interval= step.get("interval", 5)

    last_resp = None
    for attempt in range(1, retries + 1):
        try:
            resp = requests.request(method, url, json=body, headers=headers, timeout=10)
            last_resp = resp
            # try JSON, else raw text
            data = resp.json() if 'application/json' in resp.headers.get('Content-Type','') else resp.text

            # if polling a specific field:
            field = step.get("status_field")
            want  = step.get("desired_status")
            if field and want is not None:
                if isinstance(data, dict) and data.get(field) == want:
                    return {"code": 0, "response": data, "attempt": attempt}
            else:
                # no polling field specified, treat any 2xx as success
                if resp.ok:
                    return {"code": 0, "response": data, "attempt": attempt}
        except Exception as e:
            last_resp = e

        if attempt < retries:
            time.sleep(interval)

    # all retries exhausted
    err_text = last_resp.text if hasattr(last_resp, "text") else str(last_resp)
    return {
        "code": 1,
        "error": f"Did not reach desired status '{step.get('desired_status')}' after {retries} attempts",
        "last_response": err_text
    }
