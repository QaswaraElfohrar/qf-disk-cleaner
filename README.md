# QF Disk Cleaner · منظف القرص من قسورة

Find duplicate files, the biggest files and the heaviest folders — and free space safely. Deletions go to the Recycle Bin only.
اعثر على الملفات المكررة وأكبر الملفات والمجلدات، واحذف بأمان إلى سلة المحذوفات فقط.

**Free · no ads · no telemetry · العربية / English / Français** — by [Qaswara Elfohrar IT](https://qaswaraelfohrar.com)

📥 Ready-made Windows download (portable EXE): **[apps.qaswaraelfohrar.com](https://apps.qaswaraelfohrar.com)**

## Features
- Content-based duplicates: size → first block → full SHA-256, so different files are never flagged
- One-click auto-select (keep newest / oldest / shortest path) with review before delete
- Safety: Recycle Bin only, at least one copy of every duplicate is always kept, confirmation with count and size
- Top 300 biggest files and folder sizes (depth 1–4) with share of total
- Does not follow junctions (no loops or double counting), handles Arabic file names
- Cancel any time; export duplicates to CSV (Excel-friendly UTF-8)

## Build from source
```powershell
py -3.12 -m venv .venv
.venv\Scripts\pip install -r requirements.txt
.venv\Scripts\python -m pytest
.venv\Scripts\python -m qfdisk          # run
powershell -ExecutionPolicy Bypass -File build.ps1   # -> dist$5
```

## License
MIT — see [LICENSE](LICENSE). Third-party libraries keep their own licenses (PySide6/Qt: LGPLv3).

---
<sub>برمجة قسورة الفوهرر لتقنية المعلومات — الإصدار 1</sub>
