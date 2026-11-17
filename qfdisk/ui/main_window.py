"""Main window: choose folders, scan, review duplicates / biggest files / folder sizes, move to Recycle Bin."""
from __future__ import annotations

import csv
import os
import subprocess
import sys
import threading
from datetime import datetime

from PySide6.QtCore import QObject, Qt, Signal
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtWidgets import (
    QAbstractItemView, QApplication, QComboBox, QDialog, QDoubleSpinBox, QFileDialog, QHBoxLayout, QHeaderView, QLabel,
    QListWidget, QMainWindow, QMessageBox, QProgressBar, QPushButton, QSpinBox, QTableWidget, QTableWidgetItem, QTabWidget,
    QTreeWidget, QTreeWidgetItem, QVBoxLayout, QWidget,
)

from .. import PUBLISHER, PUBLISHER_EN, __version__
from ..core import scan
from ..i18n import lang, tr
from ..settings import Settings
from . import theme


def resource(*parts: str) -> str:
    base = getattr(sys, "_MEIPASS", None) or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, *parts)


def human(n: float) -> str:
    v = float(n)
    for u in ("B", "KB", "MB", "GB", "TB"):
        if v < 1024 or u == "TB":
            return ("‎" + (f"{v:.0f} {u}" if u == "B" else f"{v:.1f} {u}"))
        v /= 1024
    return str(n)


def when(ts: float) -> str:
    return "‎" + datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M")


class Bridge(QObject):
    progress = Signal(str)
    done = Signal(object, object)


class MainWindow(QMainWindow):
    def __init__(self, app: QApplication, settings: Settings):
        super().__init__()
        self.app, self.settings = app, settings
        self.files: list = []
        self.groups: list = []
        self.stop_flag = False
        self.bridge = Bridge()
        self.bridge.progress.connect(lambda t: self.status.setText(t))
        self.bridge.done.connect(self._done)
        self.setAcceptDrops(True)
        self.setWindowIcon(QIcon(resource("assets", "icon.png")))
        self.resize(1050, 780)
        self.build()

    # ------------------------------------------------------------ layout
    def build(self):
        self.setWindowTitle(tr("title"))
        root = QWidget()
        v = QVBoxLayout(root)
        top = QHBoxLayout()
        logo = QLabel()
        logo.setPixmap(QPixmap(resource("assets", "logo.png")).scaledToHeight(44, Qt.SmoothTransformation))
        top.addWidget(logo)
        who = QLabel(f"<b style='color:#F58A1F'>{PUBLISHER if lang() == 'ar' else PUBLISHER_EN}</b><br>"
                     f"<span style='color:#8b93a3'>{tr('title')} · {tr('dev_version', v=__version__)}</span>")
        top.addWidget(who, 1)
        self.lang = QComboBox()
        for code, name in (("ar", "العربية"), ("en", "English"), ("fr", "Français")):
            self.lang.addItem(name, code)
        self.lang.setCurrentIndex(max(0, self.lang.findData(self.settings["language"])))
        self.lang.currentIndexChanged.connect(self.change_lang)
        self.theme = QComboBox()
        self.theme.addItem(tr("dark"), "dark")
        self.theme.addItem(tr("light"), "light")
        self.theme.setCurrentIndex(0 if self.settings["theme"] == "dark" else 1)
        self.theme.currentIndexChanged.connect(self.change_theme)
        ab = QPushButton(tr("about"))
        ab.clicked.connect(self.about)
        for w in (self.lang, self.theme, ab):
            top.addWidget(w)
        v.addLayout(top)

        hint = QLabel(tr("drop_hint"))
        hint.setObjectName("hint")
        v.addWidget(hint)
        row = QHBoxLayout()
        self.roots = QListWidget()
        self.roots.setMaximumHeight(90)
        for r in self.settings.get("roots", []):
            self.roots.addItem(r)
        row.addWidget(self.roots, 1)
        col = QVBoxLayout()
        b1 = QPushButton(tr("add_folder"))
        b1.clicked.connect(self.add_folder)
        b2 = QPushButton(tr("remove_folder"))
        b2.clicked.connect(self.remove_folder)
        col.addWidget(b1)
        col.addWidget(b2)
        row.addLayout(col)
        v.addLayout(row)
        opt = QHBoxLayout()
        opt.addWidget(QLabel(tr("min_size")))
        self.minmb = QDoubleSpinBox()
        self.minmb.setRange(0, 100000)
        self.minmb.setDecimals(1)
        self.minmb.setMinimumWidth(110)
        self.minmb.setValue(float(self.settings.get("min_mb", 1)))
        opt.addWidget(self.minmb)
        opt.addStretch(1)
        self.scan_btn = QPushButton(tr("scan"))
        self.scan_btn.setObjectName("primary")
        self.scan_btn.setMinimumWidth(140)
        self.scan_btn.clicked.connect(self.start_scan)
        self.stop_btn = QPushButton(tr("stop"))
        self.stop_btn.setEnabled(False)
        self.stop_btn.clicked.connect(self.stop)
        opt.addWidget(self.scan_btn)
        opt.addWidget(self.stop_btn)
        v.addLayout(opt)
        self.bar = QProgressBar()
        self.bar.setVisible(False)
        v.addWidget(self.bar)
        self.status = QLabel("")
        self.status.setWordWrap(True)
        v.addWidget(self.status)

        self.tabs = QTabWidget()
        # duplicates
        d = QWidget()
        dl = QVBoxLayout(d)
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels([tr("col_file"), tr("col_size"), tr("col_modified")])
        self.tree.setColumnWidth(0, 560)
        self.tree.itemChanged.connect(self.update_selected)
        self.tree.itemDoubleClicked.connect(lambda it, _c: self.open_folder(it.data(0, Qt.UserRole)))
        dl.addWidget(self.tree, 1)
        ar = QHBoxLayout()
        ar.addWidget(QLabel(tr("keep")))
        for rule in ("newest", "oldest", "shortest"):
            b = QPushButton(tr("keep_" + rule))
            b.clicked.connect(lambda _=False, r=rule: self.auto_select(r))
            ar.addWidget(b)
        bn = QPushButton(tr("select_none"))
        bn.clicked.connect(lambda: self.auto_select(None))
        ar.addWidget(bn)
        ar.addStretch(1)
        be = QPushButton(tr("export"))
        be.clicked.connect(self.export_csv)
        ar.addWidget(be)
        dl.addLayout(ar)
        self.sel_lbl = QLabel("")
        dl.addWidget(self.sel_lbl)
        self.rec_btn = QPushButton(tr("recycle"))
        self.rec_btn.setObjectName("primary")
        self.rec_btn.setMinimumHeight(38)
        self.rec_btn.clicked.connect(self.recycle_dups)
        dl.addWidget(self.rec_btn)
        self.tabs.addTab(d, tr("tab_dups"))
        # biggest
        b = QWidget()
        bl = QVBoxLayout(b)
        self.big = QTableWidget()
        self.big.setColumnCount(3)
        self.big.setHorizontalHeaderLabels([tr("col_file"), tr("col_size"), tr("col_modified")])
        self.big.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.big.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.big.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.big.verticalHeader().hide()
        self.big.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.big.doubleClicked.connect(lambda ix: self.open_folder(self.big.item(ix.row(), 0).data(Qt.UserRole)))
        bl.addWidget(self.big, 1)
        br = QHBoxLayout()
        bo = QPushButton(tr("open_folder"))
        bo.clicked.connect(lambda: [self.open_folder(self.big.item(i.row(), 0).data(Qt.UserRole)) for i in self.big.selectionModel().selectedRows()[:1]])
        br.addWidget(bo)
        br.addStretch(1)
        rb = QPushButton(tr("recycle"))
        rb.setObjectName("primary")
        rb.clicked.connect(self.recycle_big)
        br.addWidget(rb)
        bl.addLayout(br)
        self.tabs.addTab(b, tr("tab_big"))
        # folders
        f = QWidget()
        fl = QVBoxLayout(f)
        dr = QHBoxLayout()
        dr.addWidget(QLabel(tr("depth")))
        self.depth = QSpinBox()
        self.depth.setRange(1, 4)
        self.depth.setValue(1)
        self.depth.valueChanged.connect(self.fill_folders)
        dr.addWidget(self.depth)
        dr.addStretch(1)
        fl.addLayout(dr)
        self.fold = QTableWidget()
        self.fold.setColumnCount(4)
        self.fold.setHorizontalHeaderLabels([tr("col_folder"), tr("col_size"), tr("col_files"), tr("col_share")])
        self.fold.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.fold.verticalHeader().hide()
        self.fold.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.fold.doubleClicked.connect(lambda ix: self.open_folder(self.fold.item(ix.row(), 0).data(Qt.UserRole), select=False))
        fl.addWidget(self.fold, 1)
        self.tabs.addTab(f, tr("tab_folders"))
        v.addWidget(self.tabs, 1)
        self.setCentralWidget(root)
        if self.files:
            self.fill_all()

    def apply_look(self):
        from .. import i18n

        i18n.set_lang(self.settings["language"])
        self.app.setLayoutDirection(Qt.RightToLeft if self.settings["language"] == "ar" else Qt.LeftToRight)
        self.app.setStyleSheet(theme.stylesheet(self.settings["theme"]))

    def change_lang(self):
        self.settings["language"] = self.lang.currentData()
        self.settings.save()
        self.apply_look()
        self.build()

    def change_theme(self):
        self.settings["theme"] = self.theme.currentData()
        self.settings.save()
        self.apply_look()

    # ------------------------------------------------------------ folders
    def dragEnterEvent(self, e):
        if e.mimeData().hasUrls():
            e.acceptProposedAction()

    def dropEvent(self, e):
        for u in e.mimeData().urls():
            p = u.toLocalFile()
            if os.path.isdir(p):
                self.add_root(p)

    def add_root(self, p: str):
        p = os.path.normpath(p)
        if p not in [self.roots.item(i).text() for i in range(self.roots.count())]:
            self.roots.addItem(p)
            self.save_roots()

    def add_folder(self):
        d = QFileDialog.getExistingDirectory(self, tr("add_folder"))
        if d:
            self.add_root(d)

    def remove_folder(self):
        for it in self.roots.selectedItems():
            self.roots.takeItem(self.roots.row(it))
        self.save_roots()

    def save_roots(self):
        self.settings["roots"] = [self.roots.item(i).text() for i in range(self.roots.count())]
        self.settings["min_mb"] = self.minmb.value()
        self.settings.save()

    # ------------------------------------------------------------ scan
    def start_scan(self):
        roots = [self.roots.item(i).text() for i in range(self.roots.count())]
        if not roots:
            self.status.setText(tr("no_folder"))
            return
        self.save_roots()
        self.stop_flag = False
        self.scan_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.bar.setVisible(True)
        self.bar.setRange(0, 0)
        min_size = int(self.minmb.value() * 1024 * 1024)

        def work():
            try:
                files = scan.scan(roots, min_size, lambda n, d: self.bridge.progress.emit(tr("scanning", n=n, d=os.path.basename(d) or d)),
                                  lambda: self.stop_flag)

                def hp(a, b):
                    self.bridge.progress.emit(tr("hashing", a=a, b=b))

                groups = scan.find_duplicates(files, hp, lambda: self.stop_flag)
                self.bridge.done.emit((files, groups, roots), None)
            except scan.Cancelled:
                self.bridge.done.emit(None, "cancelled")
            except Exception as e:  # noqa: BLE001
                self.bridge.done.emit(None, e)

        threading.Thread(target=work, daemon=True).start()

    def stop(self):
        self.stop_flag = True

    def _done(self, res, err):
        self.scan_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.bar.setVisible(False)
        if err == "cancelled":
            self.status.setText(tr("cancelled"))
            return
        if err is not None:
            self.status.setText(str(err))
            return
        self.files, self.groups, self.scan_roots = res
        self.fill_all()
        self.status.setText(tr("scan_done", n=len(self.files), size=human(sum(f.size for f in self.files)), g=len(self.groups),
                               w=human(scan.wasted(self.groups))))

    def fill_all(self):
        self.fill_dups()
        self.fill_big()
        self.fill_folders()

    def fill_dups(self):
        self.tree.blockSignals(True)
        self.tree.clear()
        for g in self.groups[:2000]:
            top = QTreeWidgetItem([tr("group_title", n=len(g), size=human(g[0].size), w=human(g[0].size * (len(g) - 1))), "", ""])
            top.setFlags(Qt.ItemIsEnabled)
            f = top.font(0)
            f.setBold(True)
            top.setFont(0, f)
            for fi in sorted(g, key=lambda x: x.mtime):
                it = QTreeWidgetItem([fi.path, human(fi.size), when(fi.mtime)])
                it.setFlags(Qt.ItemIsEnabled | Qt.ItemIsUserCheckable | Qt.ItemIsSelectable)
                it.setCheckState(0, Qt.Unchecked)
                it.setData(0, Qt.UserRole, fi.path)
                it.setToolTip(0, fi.path)
                top.addChild(it)
            self.tree.addTopLevelItem(top)
            top.setExpanded(True)
        self.tree.blockSignals(False)
        self.update_selected()

    def fill_big(self):
        top = sorted(self.files, key=lambda f: -f.size)[:300]
        self.big.setRowCount(len(top))
        for i, f in enumerate(top):
            a = QTableWidgetItem(f.path)
            a.setData(Qt.UserRole, f.path)
            self.big.setItem(i, 0, a)
            self.big.setItem(i, 1, QTableWidgetItem(human(f.size)))
            self.big.setItem(i, 2, QTableWidgetItem(when(f.mtime)))

    def fill_folders(self):
        if not self.files:
            return
        rows = []
        for r in getattr(self, "scan_roots", []):
            rows.extend(scan.folder_sizes(self.files, r, self.depth.value()))
        rows.sort(key=lambda x: -x[1])
        total = max(1, sum(f.size for f in self.files))
        self.fold.setRowCount(min(len(rows), 500))
        for i, (p, size, n) in enumerate(rows[:500]):
            a = QTableWidgetItem(p)
            a.setData(Qt.UserRole, p)
            self.fold.setItem(i, 0, a)
            self.fold.setItem(i, 1, QTableWidgetItem(human(size)))
            self.fold.setItem(i, 2, QTableWidgetItem(str(n)))
            self.fold.setItem(i, 3, QTableWidgetItem("‎" + f"{size * 100 / total:.1f}%"))

    # ------------------------------------------------------------ duplicates selection
    def checked_by_group(self):
        out = []
        for i in range(self.tree.topLevelItemCount()):
            top = self.tree.topLevelItem(i)
            g = self.groups[i]
            sel = {top.child(j).data(0, Qt.UserRole) for j in range(top.childCount()) if top.child(j).checkState(0) == Qt.Checked}
            out.append((g, sel))
        return out

    def selected_paths(self) -> list[str]:
        paths = []
        for g, sel in self.checked_by_group():
            paths.extend(scan.safe_to_delete(g, sel))
        return paths

    def update_selected(self, *_):
        paths = set(self.selected_paths())
        size = sum(f.size for g in self.groups for f in g if f.path in paths)
        self.sel_lbl.setText(tr("selected_info", n=len(paths), size=human(size)))

    def auto_select(self, rule):
        self.tree.blockSignals(True)
        for i in range(self.tree.topLevelItemCount()):
            top = self.tree.topLevelItem(i)
            keep = scan.choose_keep(self.groups[i], rule).path if rule else None
            for j in range(top.childCount()):
                it = top.child(j)
                it.setCheckState(0, Qt.Checked if (rule and it.data(0, Qt.UserRole) != keep) else Qt.Unchecked)
        self.tree.blockSignals(False)
        self.update_selected()

    # ------------------------------------------------------------ actions
    def _confirm_and_recycle(self, paths: list[str], size: int) -> bool:
        if not paths:
            self.status.setText(tr("nothing_selected"))
            return False
        if QMessageBox.question(self, tr("confirm_title"), tr("confirm_msg", n=len(paths), size=human(size))) != QMessageBox.Yes:
            return False
        moved, failed = scan.recycle(paths)
        gone = set(moved)
        self.files = [f for f in self.files if f.path not in gone]
        self.groups = [g2 for g2 in ([f for f in g if f.path not in gone] for g in self.groups) if len(g2) > 1]
        self.fill_all()
        msg = tr("recycled", n=len(moved), size=human(sum(0 for _ in moved) or size if not failed else size))
        if failed:
            msg += "\n" + tr("failed_n", n=len(failed))
        self.status.setText(msg)
        return True

    def recycle_dups(self):
        paths = self.selected_paths()
        sizes = {f.path: f.size for g in self.groups for f in g}
        self._confirm_and_recycle(paths, sum(sizes.get(p, 0) for p in paths))

    def recycle_big(self):
        rows = sorted({i.row() for i in self.big.selectionModel().selectedRows()})
        paths = [self.big.item(r, 0).data(Qt.UserRole) for r in rows]
        sizes = {f.path: f.size for f in self.files}
        self._confirm_and_recycle(paths, sum(sizes.get(p, 0) for p in paths))

    def open_folder(self, path: str, select: bool = True):
        if not path:
            return
        if os.path.isfile(path) and select:
            subprocess.Popen(["explorer", "/select,", os.path.normpath(path)])
        else:
            os.startfile(path if os.path.isdir(path) else os.path.dirname(path))  # type: ignore[attr-defined]

    def export_csv(self):
        p, _ = QFileDialog.getSaveFileName(self, tr("export"), "duplicates.csv", "CSV (*.csv)")
        if not p:
            return
        with open(p, "w", encoding="utf-8-sig", newline="") as f:
            w = csv.writer(f)
            w.writerow(["group", "path", "size", "modified"])
            for n, g in enumerate(self.groups, 1):
                for fi in g:
                    w.writerow([n, fi.path, fi.size, datetime.fromtimestamp(fi.mtime).strftime("%Y-%m-%d %H:%M:%S")])
        self.status.setText(tr("exported", p=p))

    def about(self):
        d = QDialog(self)
        d.setWindowTitle(tr("about"))
        d.setMinimumWidth(440)
        v = QVBoxLayout(d)
        logo = QLabel()
        logo.setPixmap(QPixmap(resource("assets", "logo.png")).scaledToWidth(280, Qt.SmoothTransformation))
        logo.setAlignment(Qt.AlignCenter)
        v.addWidget(logo)
        links = (f"<a href='https://qaswaraelfohrar.com'>{tr('dev_site')}</a> &nbsp;·&nbsp; "
                 f"<a href='https://apps.qaswaraelfohrar.com'>{tr('dev_apps')}</a> &nbsp;·&nbsp; "
                 f"<a href='https://www.facebook.com/QaswaraElfohrar'>{tr('dev_fb')}</a>")
        pub = PUBLISHER if lang() == "ar" else PUBLISHER_EN
        for t in (f"<h2 style='color:#F58A1F'>{pub}</h2>", tr("dev_free"), f"<b>{tr('title')}</b> &nbsp; {tr('dev_version', v=__version__)}",
                  tr("about_text"), links):
            l = QLabel(t)
            l.setAlignment(Qt.AlignCenter)
            l.setWordWrap(True)
            l.setOpenExternalLinks(True)
            v.addWidget(l)
        d.exec()
