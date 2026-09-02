"""Generate a public distribution manifest for the MU client."""
from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote

DEFAULT_EXCLUDES = {
    ".git",
    ".github",
    ".venv",
    "build",
    "dist",
    "publish",
    "manifest.json",
    "launcher",
    "tests",
    "tools",
    "config",
    "resources",
    "requirements.txt",
    "README.md",
    "GUIA_USO.md",
    "GUIA_ULTIMO_PASO.md",
    ".gitignore",
    "build.bat",
    "main.py",
    "changed_files.txt",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def is_excluded(path: Path, excludes: set[str]) -> bool:
    return any(part in excludes for part in path.parts)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--base-url", required=True)
    parser.add_argument("--exclude", action="append", default=[])
    args = parser.parse_args()
    base_url = args.base_url.rstrip("/") + "/"
    if not base_url.lower().startswith("https://"):
        raise SystemExit("--base-url debe usar HTTPS")
    root = args.root.resolve()
    output = args.output.resolve()
    excludes = DEFAULT_EXCLUDES | set(args.exclude)
    files = []
    for path in sorted(root.rglob("*")):
        if not path.is_file() or path.resolve() == output or is_excluded(path.relative_to(root), excludes):
            continue
        relative = path.relative_to(root).as_posix()
        files.append({
            "path": relative,
            "size": path.stat().st_size,
            "sha256": sha256(path),
            "url": base_url + quote(relative, safe="/"),
        })
    payload = {
        "schema": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "base_url": base_url,
        "files": files,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Generated {output} with {len(files)} file(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
