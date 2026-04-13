"""
Simple JSON file-backed key/value store.
Each collection is a separate JSON file under the data directory.
Thread-safe for single-process usage.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from threading import Lock
from typing import Any

_DATA_DIR = Path(os.getenv("DATA_DIR", "/app/data"))
_locks: dict[str, Lock] = {}


def _lock(collection: str) -> Lock:
    if collection not in _locks:
        _locks[collection] = Lock()
    return _locks[collection]


def _path(collection: str) -> Path:
    _DATA_DIR.mkdir(parents=True, exist_ok=True)
    return _DATA_DIR / f"{collection}.json"


def load(collection: str) -> dict[str, Any]:
    p = _path(collection)
    if not p.exists():
        return {}
    with _lock(collection):
        return json.loads(p.read_text())


def save(collection: str, data: dict[str, Any]) -> None:
    with _lock(collection):
        _path(collection).write_text(json.dumps(data, indent=2, default=str))


def get(collection: str, key: str) -> Any | None:
    return load(collection).get(key)


def put(collection: str, key: str, value: Any) -> None:
    data = load(collection)
    data[key] = value
    save(collection, data)


def delete(collection: str, key: str) -> bool:
    data = load(collection)
    if key not in data:
        return False
    del data[key]
    save(collection, data)
    return True


def all_values(collection: str) -> list[Any]:
    return list(load(collection).values())
