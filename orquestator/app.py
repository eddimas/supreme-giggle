import uuid
import json
import threading
from importlib import import_module
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query

from persistence import save_run, load_run
from fastapi.middleware.cors import CORSMiddleware

# Folder where workflow definitions live
WORKFLOWS = Path(__file__).parent / "workflows"

# Optional mapping of module names → Cypress folders
CYPRESS_MODULES = {
    # "smoke": "cypress/integration/smoke",
    # "feature": "cypress/integration/my-feature-tests",
}

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
      "http://localhost:3000",  # si sigues usando React
      "http://localhost:4200",  # tu Angular dev server
    ],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

def load_workflow(name: str) -> dict:
    """
    Read workflows/<name>.json and return its dict.
    """
    path = WORKFLOWS / f"{name}.json"
    if not path.exists():
        raise FileNotFoundError(f"No workflow named '{name}'")
    return json.loads(path.read_text())

def run_workflow(run_id: str):
    """
    Runs all steps in sequence. Stops on first non-zero exit code.
    """
    run = load_run(run_id)
    run["status"] = "running"
    save_run(run_id, run)

    for idx, step in enumerate(run["steps"]):
        try:
            module_name = f"integrations.{step['type']}_runner"
            mod = import_module(module_name)
            result = mod.execute(step)
        except Exception as e:
            result = {"error": str(e)}

        # reload & update state
        run = load_run(run_id)
        run["log"].append({"step": step["name"], "result": result})

        # if it failed, mark as failed and stop
        if result.get("code", 1) != 0:
            run["status"] = "failed"
            save_run(run_id, run)
            return

        # otherwise bump current pointer and persist
        run["current"] = idx + 1
        save_run(run_id, run)

    # all steps passed
    run["status"] = "completed"
    save_run(run_id, run)

@app.post("/start")
def start(
    name: str = Query(..., description="Workflow name (filename without .json)"),
):
    """
    Start a new workflow run.
    """
    try:
        wf = load_workflow(name)
    except FileNotFoundError:
        raise HTTPException(404, f"Workflow '{name}' not found")

    run_id = uuid.uuid4().hex
    run = {
        "id": run_id,
        "name": name,
        "steps": wf["steps"],
        "current": 0,
        "status": "pending",
        "log": []
    }
    save_run(run_id, run)

    # launch the whole sequence in a background thread
    threading.Thread(target=run_workflow, args=(run_id,), daemon=True).start()

    return {"run_id": run_id}

@app.get("/status/{run_id}")
def status(run_id: str):
    """
    Fetch the current state of a run.
    """
    try:
        return load_run(run_id)
    except FileNotFoundError:
        raise HTTPException(404, "Run not found")
