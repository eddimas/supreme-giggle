import json
import os
from pathlib import Path

class _Config:
    """
    Lazy, one-time JSON loader.
    Access keys as attributes or dict items.
    """

    _raw_json_cache: dict | None = None      # class-level cache

    def __init__(self, env: str | None = None, file: str | Path = ".env.json") -> None:
        self._env = env or os.getenv("APP_ENV", "dev")

        # load once, share across all instances
        if _Config._raw_json_cache is None:
            with open(file, "r", encoding="utf-8") as fh:
                _Config._raw_json_cache = json.load(fh)

        try:
            self._data = _Config._raw_json_cache[self._env]
        except KeyError as exc:
            raise ValueError(f"Environment '{self._env}' not found in {file}") from exc

    # --- sugar so you can do cfg["username"] or cfg.username ------------
    def __getitem__(self, key):
        return self._data[key]

    def __getattr__(self, item):
        try:
            return self._data[item]
        except KeyError as exc:
            raise AttributeError(item) from exc

    # helpful when you want the whole dict
    @property
    def as_dict(self):
        return self._data


# single shared instance; import this where you need it
cfg = _Config()          # uses APP_ENV (default "dev")