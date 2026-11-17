"""Site screenshots from a SYNTHETIC folder tree (never the owner's real files)."""
import os, sys, tempfile, random
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication
from qfdisk import i18n
from qfdisk.settings import Settings
from qfdisk.ui.main_window import MainWindow
lang, theme, out = sys.argv[1], sys.argv[2], sys.argv[3]
root = tempfile.mkdtemp(prefix="qfdisk-demo-")
rnd = random.Random(1)
def mk(rel, size, mtime=None, blob=None):
    p = os.path.join(root, rel); os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, "wb").write(blob or rnd.randbytes(size))
    if mtime: os.utime(p, (mtime, mtime))
for name, size in (("Videos/holiday.mp4", 48_000_000), ("Photos/2025/IMG_0001.jpg", 6_000_000), ("Documents/report-final.pdf", 9_000_000), ("Backups/site.zip", 30_000_000), ("Music/album.flac", 22_000_000)):
    blob = rnd.randbytes(size)
    mk(name, size, 1_700_000_000, blob)
    base, ext = os.path.splitext(name)
    mk(base + " - copy" + ext, size, 1_730_000_000, blob)
    if size > 20_000_000: mk("Downloads/" + os.path.basename(name), size, 1_735_000_000, blob)
for i in range(6): mk(f"Downloads/setup{i}.exe", rnd.randint(2_000_000, 12_000_000))
app = QApplication([])
s = Settings(); s["language"] = lang; s["theme"] = theme; s["roots"] = [root]; s["min_mb"] = 1
i18n.set_lang(lang)
w = MainWindow(app, s); w.apply_look(); w.show()
QTimer.singleShot(300, w.start_scan)
state = {"n": 0}
def tick():
    if w.files:
        w.auto_select("newest"); w.grab().save(out); print("saved", out, len(w.groups)); app.quit()
t = QTimer(); t.timeout.connect(tick); t.start(1000)
app.exec()
