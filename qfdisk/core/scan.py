"""Scanning, duplicate detection and safe deletion (Recycle Bin only)."""
from __future__ import annotations

import hashlib
import os
import stat
from collections import defaultdict
from dataclasses import dataclass
from typing import Callable, Iterable, Optional

CHUNK = 1024 * 1024
HEAD = 64 * 1024


@dataclass
class FileInfo:
    path: str
    size: int
    mtime: float


class Cancelled(Exception):
    pass


def _is_reparse(st) -> bool:
    return bool(getattr(st, "st_file_attributes", 0) & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400))


def scan(roots: Iterable[str], min_size: int = 0, progress: Optional[Callable[[int, str], None]] = None,
         cancel: Optional[Callable[[], bool]] = None) -> list[FileInfo]:
    """Walk the folders. Symlinks / junctions are not followed (no loops, no double counting)."""
    out: list[FileInfo] = []
    seen_roots = set()
    stack = []
    for r in roots:
        r = os.path.abspath(r)
        if r not in seen_roots and os.path.isdir(r):
            seen_roots.add(r)
            stack.append(r)
    n = 0
    while stack:
        if cancel and cancel():
            raise Cancelled()
        d = stack.pop()
        try:
            it = os.scandir(d)
        except OSError:
            continue
        with it:
            for e in it:
                try:
                    st = e.stat(follow_symlinks=False)
                    if e.is_symlink() or _is_reparse(st):
                        continue
                    if e.is_dir(follow_symlinks=False):
                        stack.append(e.path)
                    elif e.is_file(follow_symlinks=False) and st.st_size >= min_size:
                        out.append(FileInfo(e.path, st.st_size, st.st_mtime))
                        n += 1
                        if progress and n % 500 == 0:
                            progress(n, d)
                except OSError:
                    continue
    # the same file can be reached through overlapping roots
    uniq = {os.path.normcase(f.path): f for f in out}
    return list(uniq.values())


def _hash(path: str, limit: Optional[int] = None) -> Optional[str]:
    h = hashlib.sha256()
    try:
        with open(path, "rb") as f:
            if limit is not None:
                h.update(f.read(limit))
            else:
                for block in iter(lambda: f.read(CHUNK), b""):
                    h.update(block)
    except OSError:
        return None
    return h.hexdigest()


def find_duplicates(files: list[FileInfo], progress: Optional[Callable[[int, int], None]] = None,
                    cancel: Optional[Callable[[], bool]] = None) -> list[list[FileInfo]]:
    """Group by size, then by the first 64 KB, then by the full SHA-256. Empty files are ignored."""
    by_size: dict[int, list[FileInfo]] = defaultdict(list)
    for f in files:
        if f.size > 0:
            by_size[f.size].append(f)
    cands = [g for g in by_size.values() if len(g) > 1]
    total = sum(len(g) for g in cands) * 2
    done = 0
    groups: list[list[FileInfo]] = []
    for g in cands:
        by_head: dict[str, list[FileInfo]] = defaultdict(list)
        for f in g:
            if cancel and cancel():
                raise Cancelled()
            h = _hash(f.path, HEAD)
            done += 1
            if h:
                by_head[h].append(f)
        for gh in by_head.values():
            if len(gh) < 2:
                done += len(gh)
                continue
            by_full: dict[str, list[FileInfo]] = defaultdict(list)
            for f in gh:
                if cancel and cancel():
                    raise Cancelled()
                h = _hash(f.path)
                done += 1
                if progress:
                    progress(done, total)
                if h:
                    by_full[h].append(f)
            groups.extend(x for x in by_full.values() if len(x) > 1)
    groups.sort(key=lambda g: -g[0].size * (len(g) - 1))
    return groups


def wasted(groups: list[list[FileInfo]]) -> int:
    return sum(g[0].size * (len(g) - 1) for g in groups)


def folder_sizes(files: list[FileInfo], root: str, depth: int = 1) -> list[tuple[str, int, int]]:
    """Size of every sub-folder `depth` levels under root: (path, bytes, file count), biggest first."""
    root = os.path.abspath(root)
    acc: dict[str, list[int]] = defaultdict(lambda: [0, 0])
    for f in files:
        rel = os.path.relpath(f.path, root)
        if rel.startswith(".."):
            continue
        parts = rel.split(os.sep)
        key = os.path.join(root, *parts[:depth]) if len(parts) > depth else root
        acc[key][0] += f.size
        acc[key][1] += 1
    return sorted(((k, v[0], v[1]) for k, v in acc.items()), key=lambda x: -x[1])


def choose_keep(group: list[FileInfo], rule: str) -> FileInfo:
    """Which copy to keep: newest | oldest | shortest (shortest path, then oldest)."""
    if rule == "newest":
        return max(group, key=lambda f: f.mtime)
    if rule == "oldest":
        return min(group, key=lambda f: f.mtime)
    return min(group, key=lambda f: (len(f.path), f.mtime))


def safe_to_delete(group: list[FileInfo], selected: set[str]) -> list[str]:
    """Paths of the group that may be deleted: never all of them (one copy always stays)."""
    paths = [f.path for f in group if f.path in selected]
    if len(paths) >= len(group):
        paths = paths[:-1]
    return paths


def recycle(paths: list[str]) -> tuple[list[str], list[tuple[str, str]]]:
    """Move to the Recycle Bin (never a permanent delete). Returns (moved, failed[(path, reason)])."""
    from send2trash import send2trash

    moved, failed = [], []
    for p in paths:
        try:
            send2trash(os.path.normpath(p))
            moved.append(p)
        except Exception as e:  # noqa: BLE001
            failed.append((p, str(e)))
    return moved, failed
