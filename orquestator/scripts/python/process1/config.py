# config.py
import json
import os
import functools        # ← este faltaba
from pathlib import Path


class _Config:
    """
    Lazy-loader JSON.
    Acceso por atributo (cfg.user) o dict (cfg["user"]).
    """

    _raw_json_cache: dict | None = None

    def __init__(self, env: str | None = None, file: str | Path = ".env.json") -> None:
        self._env = env or os.getenv("APP_ENV", "dev")

        # ⇒ carga el JSON solo una vez por proceso
        if _Config._raw_json_cache is None:
            with open(file, "r", encoding="utf-8") as fh:
                _Config._raw_json_cache = json.load(fh)

        try:
            self._data = _Config._raw_json_cache[self._env]
        except KeyError as exc:
            raise ValueError(f"Environment '{self._env}' not found in {file}") from exc

    # azúcar sintáctico
    def __getitem__(self, key):         # cfg["token"]
        return self._data[key]

    def __getattr__(self, item):        # cfg.token
        try:
            return self._data[item]
        except KeyError as exc:
            raise AttributeError(item) from exc

    @property
    def as_dict(self):                  # cfg.as_dict -> dict completo
        return self._data


# --------------------------------------------------------------------------- #
# Decorador opcional para inyectar cfg en cualquier función
def with_config(env: str | None = None, param_name: str = "cfg"):
    """
    Uso:
        @with_config()      -> usa APP_ENV (o 'dev')
        @with_config("uat") -> fuerza 'uat'
    """
    def deco(func):
        cfg_obj = _Config(env)

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            kwargs.setdefault(param_name, cfg_obj)
            return func(*args, **kwargs)
        return wrapper
    return deco


# Singleton global (útil para scripts rápidos: from config import cfg)
cfg = _Config()             # respeta APP_ENV