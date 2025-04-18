import json
from pathlib import Path
from threading import Lock

# Directory for run‑state files
_STATE_DIR = Path(__file__).parent / "runs"
_STATE_DIR.mkdir(exist_ok=True)

# In‑process locks to avoid concurrent writes
_locks: dict[str, Lock] = {}

def _lock_for(run_id: str) -> Lock:
    if run_id not in _locks:
        _locks[run_id] = Lock()
    return _locks[run_id]

def save_run(run_id: str, data: dict) -> None:
    """
    Persist run state to runs/<run_id>.json
    """
    path = _STATE_DIR / f"{run_id}.json"
    with _lock_for(run_id):
        with open(path, "w") as f:
            json.dump(data, f, indent=2)

def load_run(run_id: str) -> dict:
    """
    Load run state from runs/<run_id>.json
    """
    path = _STATE_DIR / f"{run_id}.json"
    with _lock_for(run_id):
        with open(path, "r") as f:
            return json.load(f)
