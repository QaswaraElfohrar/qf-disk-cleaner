import os
import time

import pytest

from qfdisk.core import scan


def w(p, data: bytes, mtime=None):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "wb") as f:
        f.write(data)
    if mtime:
        os.utime(p, (mtime, mtime))
    return str(p)


@pytest.fixture
def tree(tmp_path):
    a = w(tmp_path / "a" / "photo.jpg", b"A" * 200_000, 1_000_000)
    b = w(tmp_path / "b" / "photo copy.jpg", b"A" * 200_000, 2_000_000)
    c = w(tmp_path / "b" / "deep" / "x.jpg", b"A" * 200_000, 3_000_000)
    # same size, same first 64 KB, different tail -> NOT a duplicate
    d1 = w(tmp_path / "c" / "big1.bin", b"Z" * 100_000 + b"1" * 50_000)
    d2 = w(tmp_path / "c" / "big2.bin", b"Z" * 100_000 + b"2" * 50_000)
    w(tmp_path / "d" / "unique.txt", b"hello")
    w(tmp_path / "d" / "empty1.txt", b"")
    w(tmp_path / "d" / "empty2.txt", b"")
    return tmp_path, [a, b, c], [d1, d2]


def test_scan_and_min_size(tree):
    root, _, _ = tree
    files = scan.scan([str(root)])
    assert len(files) == 8
    big = scan.scan([str(root)], min_size=100_000)
    assert len(big) == 5


def test_duplicates_exact_only(tree):
    root, dups, near = tree
    groups = scan.find_duplicates(scan.scan([str(root)]))
    assert len(groups) == 1  # only the three photos; near-identical files and empty files are not duplicates
    assert {f.path for f in groups[0]} == set(dups)
    assert scan.wasted(groups) == 400_000


def test_overlapping_roots_do_not_create_fake_duplicates(tree):
    root, _, _ = tree
    files = scan.scan([str(root), str(root / "a"), str(root)])
    assert len(files) == 8
    assert len(scan.find_duplicates(files)) == 1


def test_choose_keep(tree):
    root, dups, _ = tree
    g = scan.find_duplicates(scan.scan([str(root)]))[0]
    assert scan.choose_keep(g, "oldest").path == dups[0]
    assert scan.choose_keep(g, "newest").path == dups[2]
    assert scan.choose_keep(g, "shortest").path == dups[0]


def test_never_deletes_every_copy(tree):
    root, dups, _ = tree
    g = scan.find_duplicates(scan.scan([str(root)]))[0]
    allsel = {f.path for f in g}
    assert len(scan.safe_to_delete(g, allsel)) == 2
    assert len(scan.safe_to_delete(g, {dups[1]})) == 1
    assert scan.safe_to_delete(g, set()) == []


def test_folder_sizes(tree):
    root, _, _ = tree
    fs = scan.folder_sizes(scan.scan([str(root)]), str(root))
    top = dict((os.path.basename(p), (s, n)) for p, s, n in fs)
    assert top["b"] == (400_000, 2) and top["a"] == (200_000, 1) and top["c"] == (300_000, 2)


def test_arabic_names_and_unreadable(tmp_path):
    a = w(tmp_path / "مجلد" / "ملف.pdf", b"x" * 5000)
    b = w(tmp_path / "نسخة" / "ملف نسخة.pdf", b"x" * 5000)
    g = scan.find_duplicates(scan.scan([str(tmp_path)]))
    assert len(g) == 1
    # a file that disappears between scan and hash is skipped, not a crash
    files = scan.scan([str(tmp_path)])
    os.remove(a)
    assert scan.find_duplicates(files) == []


def test_cancel(tree):
    root, _, _ = tree
    with pytest.raises(scan.Cancelled):
        scan.scan([str(root)], cancel=lambda: True)


def test_recycle_moves_not_deletes(tmp_path, monkeypatch):
    p = w(tmp_path / "gone.txt", b"data")
    sent = []
    import send2trash

    monkeypatch.setattr(send2trash, "send2trash", lambda x: sent.append(x))
    moved, failed = scan.recycle([p])
    assert moved == [p] and not failed and sent  # only the Recycle Bin API is ever used


def test_recycle_failure_reported(tmp_path, monkeypatch):
    import send2trash

    def boom(x):
        raise OSError("locked")

    monkeypatch.setattr(send2trash, "send2trash", boom)
    moved, failed = scan.recycle([str(tmp_path / "x")])
    assert not moved and failed and "locked" in failed[0][1]
