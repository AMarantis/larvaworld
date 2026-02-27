from __future__ import annotations

import json
import os
import shutil
from pathlib import Path
from urllib.parse import quote

from larvaworld.portal.landing_registry import NOTEBOOK_TUTORIAL_BY_ITEM_ID


_REPO_ROOT = Path(__file__).resolve().parents[3]
_TUTORIALS_DIR = _REPO_ROOT / "docs" / "tutorials"
_NOTEBOOK_URLS_CACHE: dict[str, str] | None = None


def _workspace_dir() -> Path:
    # English comments inside code.
    raw = os.getenv("LARVAWORLD_PORTAL_NOTEBOOK_WORKSPACE")
    if raw:
        return Path(raw).expanduser().resolve()
    return (_REPO_ROOT / ".portal_notebooks").resolve()


def _kernel_name() -> str:
    # English comments inside code.
    kernel = os.getenv("LARVAWORLD_PORTAL_NOTEBOOK_KERNEL", "python3").strip()
    return kernel or "python3"


def _jupyter_base_url() -> str:
    # English comments inside code.
    base = os.getenv("LARVAWORLD_JUPYTER_BASE_URL", "http://localhost:8888").strip()
    return base.rstrip("/") or "http://localhost:8888"


def _jupyter_root_dir() -> Path:
    # English comments inside code.
    raw = os.getenv("LARVAWORLD_JUPYTER_ROOT_DIR")
    if raw:
        return Path(raw).expanduser().resolve()
    return _REPO_ROOT


def _normalize_notebook_kernel(notebook_path: Path, *, kernel_name: str) -> None:
    # English comments inside code.
    try:
        notebook = json.loads(notebook_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return

    metadata = notebook.setdefault("metadata", {})
    metadata["kernelspec"] = {
        "display_name": kernel_name,
        "language": "python",
        "name": kernel_name,
    }
    language_info = metadata.setdefault("language_info", {})
    if isinstance(language_info, dict):
        language_info["name"] = "python"

    notebook_path.write_text(
        json.dumps(notebook, ensure_ascii=False, indent=1) + "\n",
        encoding="utf-8",
    )


def _build_jupyter_url(notebook_path: Path) -> str:
    # English comments inside code.
    jupyter_root = _jupyter_root_dir()
    try:
        relative = notebook_path.resolve().relative_to(jupyter_root)
        notebook_ref = relative.as_posix()
    except ValueError:
        notebook_ref = notebook_path.resolve().as_posix()
    return f"{_jupyter_base_url()}/lab/tree/{quote(notebook_ref)}"


def _prepare_notebook_urls() -> dict[str, str]:
    # English comments inside code.
    workspace_dir = _workspace_dir()
    workspace_dir.mkdir(parents=True, exist_ok=True)
    kernel = _kernel_name()

    urls: dict[str, str] = {}
    for item_id, notebook_name in NOTEBOOK_TUTORIAL_BY_ITEM_ID.items():
        source = _TUTORIALS_DIR / notebook_name
        if not source.exists():
            continue

        target = workspace_dir / f"{item_id.replace('.', '_')}.ipynb"
        try:
            shutil.copy2(source, target)
        except OSError:
            continue
        _normalize_notebook_kernel(target, kernel_name=kernel)
        urls[item_id] = _build_jupyter_url(target)

    return urls


def notebook_urls_by_item() -> dict[str, str]:
    # English comments inside code.
    global _NOTEBOOK_URLS_CACHE
    if _NOTEBOOK_URLS_CACHE is None:
        _NOTEBOOK_URLS_CACHE = _prepare_notebook_urls()
    return _NOTEBOOK_URLS_CACHE
