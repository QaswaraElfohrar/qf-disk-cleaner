import sys


def cli_scan(folder: str) -> int:
    """`QFDisk.exe --scan <folder>`: prints duplicate groups (self-test of the built exe)."""
    from .core import scan

    files = scan.scan([folder])
    groups = scan.find_duplicates(files)
    print(f"files={len(files)} duplicate_groups={len(groups)} wasted={scan.wasted(groups)}")
    return 0


def main() -> int:
    if len(sys.argv) > 2 and sys.argv[1] == "--scan":
        return cli_scan(sys.argv[2])
    from PySide6.QtGui import QIcon
    from PySide6.QtWidgets import QApplication

    from . import i18n
    from .settings import Settings
    from .ui.main_window import MainWindow, resource

    app = QApplication(sys.argv[:1])
    app.setWindowIcon(QIcon(resource("assets", "icon.png")))
    st = Settings()
    i18n.set_lang(st["language"])
    win = MainWindow(app, st)
    win.apply_look()
    win.show()
    return app.exec()
