"""
src/content/loader.py

Two loaders:
  content_for("index")  → src/content/page/index.yaml    → template var: content
  shared("nav")         → src/content/shared/nav.yaml     → template var: nav (etc.)
"""

from pathlib import Path
import yaml

_ROOT        = Path(__file__).resolve().parent
_PAGE_ROOT   = _ROOT / "page"
_SHARED_ROOT = _ROOT / "shared"

_cache: dict[str, dict] = {}


def _load(path: Path, cache_key: str) -> dict:
    if cache_key not in _cache:
        if not path.exists():
            raise FileNotFoundError(f"Content file not found: {path}")
        with path.open(encoding="utf-8") as f:
            _cache[cache_key] = yaml.safe_load(f) or {}
    return _cache[cache_key]


def content_for(page: str) -> dict:
    """
    Load src/content/page/{page}.yaml.
    Unpacks into template context as `content`.

        **content_for("index")  →  {{ content.hero.title }}
    """
    path = _PAGE_ROOT / f"{page}.yaml"
    return {"content": _load(path, f"page:{page}")}


def shared(name: str) -> dict:
    """
    Load src/content/shared/{name}.yaml.
    Unpacks into template context under the file's own name.

        **shared("nav")  →  {{ nav.links }}, {{ nav.header }}
    """
    path = _SHARED_ROOT / f"{name}.yaml"
    return {name: _load(path, f"shared:{name}")}


def reload(key: str | None = None) -> None:
    """Bust cache for one key or everything."""
    if key is None:
        _cache.clear()
    else:
        _cache.pop(key, None)