"""Arabic / English / French strings: key -> (ar, en, fr)."""
from __future__ import annotations

_idx = 0
_CODES = {"ar": 0, "en": 1, "fr": 2}

S: dict[str, tuple[str, str, str]] = {
    "title": ("منظف القرص من قسورة", "QF Disk Cleaner", "QF Disk Cleaner"),
    "add_folder": ("إضافة مجلد...", "Add folder...", "Ajouter un dossier..."),
    "remove_folder": ("حذف المجلد المحدد", "Remove selected folder", "Retirer le dossier"),
    "min_size": ("تجاهل الملفات الأصغر من (ميجا)", "Ignore files smaller than (MB)", "Ignorer les fichiers de moins de (Mo)"),
    "scan": ("ابدأ الفحص", "Scan", "Analyser"),
    "stop": ("إيقاف", "Stop", "Arrêter"),
    "drop_hint": ("أضف المجلدات اللي عايز تفحصها (أو اسحبها هنا)", "Add the folders to scan (or drop them here)", "Ajoutez les dossiers à analyser (ou déposez-les ici)"),
    "tab_dups": ("الملفات المكررة", "Duplicates", "Doublons"),
    "tab_big": ("أكبر الملفات", "Largest files", "Plus gros fichiers"),
    "tab_folders": ("حجم المجلدات", "Folder sizes", "Taille des dossiers"),
    "scanning": ("جاري الفحص... {n} ملف ({d})", "Scanning... {n} files ({d})", "Analyse... {n} fichiers ({d})"),
    "hashing": ("مقارنة المحتوى... {a} من {b}", "Comparing content... {a} of {b}", "Comparaison du contenu... {a} sur {b}"),
    "scan_done": ("تم فحص {n} ملف ({size}). {g} مجموعة مكررة، المساحة المهدرة {w}.", "Scanned {n} files ({size}). {g} duplicate groups, {w} wasted.", "{n} fichiers analysés ({size}). {g} groupes de doublons, {w} gaspillés."),
    "cancelled": ("تم إيقاف الفحص.", "Scan stopped.", "Analyse arrêtée."),
    "keep": ("اختيار تلقائي، وأبقي:", "Auto-select, keep:", "Sélection auto, garder :"),
    "keep_newest": ("الأحدث", "the newest", "le plus récent"),
    "keep_oldest": ("الأقدم", "the oldest", "le plus ancien"),
    "keep_shortest": ("أقصر مسار", "the shortest path", "le chemin le plus court"),
    "select_none": ("إلغاء التحديد", "Select none", "Tout désélectionner"),
    "recycle": ("نقل المحدد لسلة المحذوفات", "Move selected to Recycle Bin", "Mettre la sélection à la corbeille"),
    "selected_info": ("المحدد: {n} ملف ({size})", "Selected: {n} file(s) ({size})", "Sélection : {n} fichier(s) ({size})"),
    "confirm_title": ("تأكيد", "Confirm", "Confirmation"),
    "confirm_msg": ("هتنقل {n} ملف ({size}) لسلة المحذوفات؟\nتقدر ترجّعهم منها. وفي كل مجموعة مكررة بتفضل نسخة واحدة على الأقل.", "Move {n} file(s) ({size}) to the Recycle Bin?\nYou can restore them from there. Every duplicate group keeps at least one copy.", "Mettre {n} fichier(s) ({size}) à la corbeille ?\nVous pouvez les restaurer. Chaque groupe garde au moins une copie."),
    "recycled": ("تم نقل {n} ملف ({size}) لسلة المحذوفات.", "Moved {n} file(s) ({size}) to the Recycle Bin.", "{n} fichier(s) ({size}) mis à la corbeille."),
    "failed_n": ("تعذر نقل {n} ملف (مفتوح أو بدون صلاحية).", "{n} file(s) could not be moved (in use or no permission).", "{n} fichier(s) n'ont pas pu être déplacés (utilisés ou sans droits)."),
    "nothing_selected": ("حدّد ملفات الأول.", "Select files first.", "Sélectionnez d'abord des fichiers."),
    "no_folder": ("أضف مجلد الأول.", "Add a folder first.", "Ajoutez d'abord un dossier."),
    "col_file": ("الملف", "File", "Fichier"),
    "col_size": ("الحجم", "Size", "Taille"),
    "col_modified": ("آخر تعديل", "Modified", "Modifié"),
    "col_folder": ("المجلد", "Folder", "Dossier"),
    "col_files": ("عدد الملفات", "Files", "Fichiers"),
    "col_share": ("النسبة", "Share", "Part"),
    "group_title": ("{n} نسخ × {size} — مهدر {w}", "{n} copies × {size} — {w} wasted", "{n} copies × {size} — {w} gaspillés"),
    "open_folder": ("فتح مكان الملف", "Show in folder", "Afficher dans le dossier"),
    "depth": ("العمق", "Depth", "Profondeur"),
    "export": ("تصدير CSV", "Export CSV", "Exporter CSV"),
    "exported": ("تم الحفظ: {p}", "Saved: {p}", "Enregistré : {p}"),
    "about": ("عن المبرمج", "About the developer", "À propos du développeur"),
    "dev_free": ("برامج مجانية، بدون إعلانات ولا تتبع", "Free programs, no ads, no tracking", "Logiciels gratuits, sans publicité ni suivi"),
    "dev_site": ("الموقع الرسمي", "Official website", "Site officiel"),
    "dev_apps": ("كل برامج قسورة (تحميل مجاني)", "All Qaswara programs (free download)", "Tous les logiciels Qaswara (gratuits)"),
    "dev_fb": ("صفحة فيسبوك", "Facebook page", "Page Facebook"),
    "dev_version": ("الإصدار {v}", "Version {v}", "Version {v}"),
    "about_text": ("برنامج محمول بيدوّر على الملفات المكررة وأكبر الملفات والمجلدات اللي واخدة مساحة. مفيش حاجة بتتمسح نهائيًا: كل شيء بيروح لسلة المحذوفات.", "A portable program that finds duplicate files, the largest files and the folders using the most space. Nothing is permanently deleted: everything goes to the Recycle Bin.", "Programme portable qui trouve les doublons, les plus gros fichiers et les dossiers les plus volumineux. Rien n'est supprimé définitivement : tout va à la corbeille."),
    "language": ("اللغة", "Language", "Langue"),
    "dark": ("داكن", "Dark", "Sombre"),
    "light": ("فاتح", "Light", "Clair"),
}


def set_lang(code: str) -> None:
    global _idx
    _idx = _CODES.get(code, 0)


def lang() -> str:
    return ["ar", "en", "fr"][_idx]


def tr(key: str, **kw) -> str:
    t = S.get(key)
    if t is None:
        return key
    s = t[_idx]
    return s.format(**kw) if kw else s
