"""Purge jsDelivr's GitHub CDN cache for files changed in a publish.

jsDelivr caches files served from a mutable ref (a branch like @main) for up
to 7 days. After pushing new client files and regenerating manifest.json,
call this script so players see the update immediately instead of a stale
cached copy. No credentials required: purge.jsdelivr.net is a public,
unauthenticated endpoint.
"""
from __future__ import annotations

import argparse
import time
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

PURGE_BASE = "https://purge.jsdelivr.net/gh"
USER_AGENT = "MU-Launcher-Publisher/1.0"


def purge_one(owner_repo_ref: str, path: str, timeout: float = 15.0) -> None:
    url = f"{PURGE_BASE}/{owner_repo_ref}/{quote(path, safe='/')}"
    request = Request(url, headers={"User-Agent": USER_AGENT}, method="GET")
    try:
        with urlopen(request, timeout=timeout) as response:
            print(f"[purge] {path}: HTTP {response.status}")
    except HTTPError as exc:
        # A 404 here just means jsDelivr had nothing cached for that path yet.
        print(f"[purge] {path}: HTTP {exc.code} (ignorado)")
    except (URLError, TimeoutError) as exc:
        print(f"[purge] {path}: error de red ({exc}) (ignorado)")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--owner-repo-ref", required=True, help="owner/repo@ref, ej: Tiinita/MU-UPDATE@main")
    parser.add_argument("--file", action="append", default=[], help="Ruta puntual a purgar (puede repetirse)")
    parser.add_argument("--list", type=Path, help="Archivo de texto con una ruta relativa por línea")
    parser.add_argument(
        "--rounds", type=int, default=2,
        help="Cuántas veces purgar cada ruta (default 2). jsDelivr purga primero sus servidores "
             "de borde, pero el origen interno puede tardar unos segundos más en actualizarse; "
             "una sola purga puede devolver momentáneamente una versión vieja. Repetir la purga "
             "mitiga esto sin garantizarlo por completo.",
    )
    parser.add_argument("--round-delay", type=float, default=6.0, help="Segundos de espera entre rondas de purga")
    args = parser.parse_args()

    paths = list(dict.fromkeys(args.file))  # de-dup, preserve order
    if args.list and args.list.exists():
        extra = [line.strip() for line in args.list.read_text(encoding="utf-8").splitlines() if line.strip()]
        for path in extra:
            if path not in paths:
                paths.append(path)

    if not paths:
        print("No hay rutas para purgar.")
        return 0

    rounds = max(1, args.rounds)
    for round_number in range(1, rounds + 1):
        print(f"[purge] Ronda {round_number}/{rounds}")
        for path in paths:
            purge_one(args.owner_repo_ref, path)
            time.sleep(0.2)  # evita ráfagas innecesarias contra el endpoint público
        if round_number < rounds:
            time.sleep(args.round_delay)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
