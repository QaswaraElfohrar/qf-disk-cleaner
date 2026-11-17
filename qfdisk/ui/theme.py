ACCENT = "#F58A1F"

_COMMON = """
* { font-family: 'Segoe UI', 'Tahoma', sans-serif; font-size: 10pt; }
QPushButton, QToolButton { border-radius: 6px; padding: 6px 12px; }
QLineEdit, QPlainTextEdit, QSpinBox, QComboBox, QDateTimeEdit, QTimeEdit { border-radius: 6px; padding: 5px 8px; }
QHeaderView::section { padding: 6px 8px; border: none; font-weight: 600; }
QProgressBar { border-radius: 5px; text-align: center; }
QProgressBar::chunk { border-radius: 5px; background: %(a)s; }
QMenu::item { padding: 6px 22px; }
QToolBar { spacing: 4px; padding: 4px; }
QListWidget::item { padding: 7px 10px; border-radius: 6px; margin: 1px 4px; }
QTabBar::tab { padding: 8px 16px; }
QSlider::groove:horizontal { height: 6px; background: #8884; border-radius: 3px; }
QSlider::sub-page:horizontal { background: %(a)s; border-radius: 3px; }
QSlider::handle:horizontal { background: %(a)s; width: 16px; margin: -6px 0; border-radius: 8px; }
"""

DARK = """
QWidget { background: #14171d; color: #e8ebf0; }
QMainWindow, QDialog { background: #14171d; }
QToolBar { background: #1a1e26; border: none; border-bottom: 1px solid #262b35; }
QPushButton, QToolButton { background: #242a35; border: 1px solid #323948; color: #e8ebf0; }
QPushButton:hover, QToolButton:hover { background: #2d3441; border-color: %(a)s; }
QPushButton:default, QPushButton#primary { background: %(a)s; color: #1b1100; border: none; font-weight: 700; }
QPushButton:disabled, QToolButton:disabled { color: #6b7280; background: #1b1f27; }
QLineEdit, QPlainTextEdit, QSpinBox, QComboBox, QDateTimeEdit, QTimeEdit { background: #1d222b; border: 1px solid #323948; selection-background-color: %(a)s; selection-color: #1b1100; }
QComboBox QAbstractItemView { background: #1d222b; selection-background-color: %(a)s; selection-color: #1b1100; }
QTableView { background: #171b22; alternate-background-color: #1a1f27; gridline-color: #232935; border: none; selection-background-color: #3a2a14; selection-color: #ffe9cf; }
QHeaderView::section { background: #1a1e26; color: #aeb6c4; }
QListWidget { background: #171b22; border: none; border-right: 1px solid #262b35; outline: none; }
QListWidget::item:selected { background: #3a2a14; color: #ffb35c; }
QListWidget::item:hover { background: #20252e; }
QStatusBar { background: #1a1e26; color: #aeb6c4; border-top: 1px solid #262b35; }
QProgressBar { background: #232935; border: none; color: #fff; }
QMenu { background: #1d222b; border: 1px solid #323948; }
QMenu::item:selected { background: %(a)s; color: #1b1100; }
QTabWidget::pane { border: 1px solid #323948; border-radius: 6px; }
QTabBar::tab { background: #1a1e26; color: #aeb6c4; }
QTabBar::tab:selected { color: %(a)s; border-bottom: 2px solid %(a)s; }
QCheckBox::indicator, QRadioButton::indicator { width: 16px; height: 16px; }
QToolTip { background: #242a35; color: #fff; border: 1px solid %(a)s; }
QLabel#hint { color: #8b93a3; }
QLabel#warn { color: #ff7b6b; }
"""

LIGHT = """
QWidget { background: #f6f7f9; color: #1c2230; }
QMainWindow, QDialog { background: #f6f7f9; }
QToolBar { background: #ffffff; border: none; border-bottom: 1px solid #e0e4ea; }
QPushButton, QToolButton { background: #ffffff; border: 1px solid #cfd5df; color: #1c2230; }
QPushButton:hover, QToolButton:hover { background: #fff4e6; border-color: %(a)s; }
QPushButton:default, QPushButton#primary { background: %(a)s; color: #ffffff; border: none; font-weight: 700; }
QPushButton:disabled, QToolButton:disabled { color: #9aa3b2; background: #eef0f4; }
QLineEdit, QPlainTextEdit, QSpinBox, QComboBox, QDateTimeEdit, QTimeEdit { background: #ffffff; border: 1px solid #cfd5df; selection-background-color: %(a)s; selection-color: #fff; }
QComboBox QAbstractItemView { background: #ffffff; selection-background-color: %(a)s; selection-color: #fff; }
QTableView { background: #ffffff; alternate-background-color: #f6f8fb; gridline-color: #e6e9ef; border: none; selection-background-color: #ffe7c9; selection-color: #3a2400; }
QHeaderView::section { background: #eef1f5; color: #4a5365; }
QListWidget { background: #ffffff; border: none; border-right: 1px solid #e0e4ea; outline: none; }
QListWidget::item:selected { background: #ffe7c9; color: #b25c00; }
QListWidget::item:hover { background: #f1f3f7; }
QStatusBar { background: #ffffff; color: #4a5365; border-top: 1px solid #e0e4ea; }
QProgressBar { background: #e6e9ef; border: none; color: #1c2230; }
QMenu { background: #ffffff; border: 1px solid #cfd5df; }
QMenu::item:selected { background: %(a)s; color: #fff; }
QTabWidget::pane { border: 1px solid #cfd5df; border-radius: 6px; }
QTabBar::tab { background: #eef1f5; color: #4a5365; }
QTabBar::tab:selected { color: %(a)s; border-bottom: 2px solid %(a)s; }
QLabel#hint { color: #6b7385; }
QLabel#warn { color: #c0392b; }
"""


def stylesheet(name: str) -> str:
    return (_COMMON + (LIGHT if name == "light" else DARK)) % {"a": ACCENT}
