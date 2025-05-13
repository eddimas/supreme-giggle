#!/usr/bin/env python3
"""
Example usage:
    python myScript.py --env dev --trans_id 20934djjd9a
"""

import argparse
import json
import os
import requests          # or httpx, urllib, etc.

from utils import with_config        # where you defined the decorator


# --- STEP 1: Pure business logic -------------------------------------------
@with_config()                        # cfg will be auto-injected
def fetch_transaction(trans_id: str, *, cfg):
    """
    Makes the API request and returns the server JSON.
    Relies on keys living in env.json, e.g. cfg.base_url, cfg.token …
    """
    url = f"{cfg.base_url}/transactions/{trans_id}"
    headers = {"Authorization": f"Bearer {cfg.token}"}

    r = requests.get(url, headers=headers, timeout=10)
    r.raise_for_status()
    return r.json()                   # e.g. {"status": "success", "code": 200}


# --- STEP 2: CLI plumbing ---------------------------------------------------
def parse_cli():
    p = argparse.ArgumentParser(description="Small API helper")
    p.add_argument(
        "--env",
        choices=["dev", "uat", "prod"],
        help="Which block inside env.json to use (default: dev)",
    )
    p.add_argument(
        "--trans_id",
        required=True,
        help="Transaction ID to query (e.g. 20934djjd9a)",
    )
    return p.parse_args()


def main() -> None:
    args = parse_cli()

    if args.env:
        os.environ["APP_ENV"] = args.env

    result = fetch_transaction(args.trans_id)

    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()