"""
backup_index.py
----------------
سكريبت لعمل نسخة احتياطية من فهرس FAISS والبيانات الوصفية المرتبطة به.

الاستخدام:
    python scripts/backup_index.py
    python scripts/backup_index.py --keep 5   # الاحتفاظ بآخر 5 نسخ فقط
"""

import argparse
import logging
import shutil
import sys
from datetime import datetime
from pathlib import Path

# ============================================
# المسارات الأساسية
# ============================================
ROOT_DIR = Path(__file__).resolve().parent.parent
FAISS_INDEX_DIR = ROOT_DIR / "faiss_index"
BACKUP_ROOT_DIR = ROOT_DIR / "data" / "backups" / "faiss_backup"

# الملفات المطلوب نسخها من فهرس FAISS
INDEX_FILES = [
    "index.faiss",
    "metadata.pkl",
    "file_mapping.json",
    "index_config.json",
]

# ============================================
# إعداد نظام التسجيل (Logging)
# ============================================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("backup_index")


def create_backup() -> Path:
    """ينسخ ملفات فهرس FAISS الحالية إلى مجلد نسخ احتياطية بتوقيت زمني."""
    if not FAISS_INDEX_DIR.exists():
        logger.error("مجلد الفهرس غير موجود: %s", FAISS_INDEX_DIR)
        sys.exit(1)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = BACKUP_ROOT_DIR / f"backup_{timestamp}"
    backup_dir.mkdir(parents=True, exist_ok=True)

    copied_files = []
    missing_files = []

    for filename in INDEX_FILES:
        source_path = FAISS_INDEX_DIR / filename
        if source_path.exists():
            shutil.copy2(source_path, backup_dir / filename)
            copied_files.append(filename)
        else:
            missing_files.append(filename)

    if not copied_files:
        logger.error("لم يتم العثور على أي ملفات فهرس لنسخها.")
        backup_dir.rmdir()
        sys.exit(1)

    if missing_files:
        logger.warning("ملفات غير موجودة تم تجاهلها: %s", ", ".join(missing_files))

    logger.info("تم إنشاء نسخة احتياطية بنجاح في: %s", backup_dir)
    logger.info("الملفات المنسوخة: %s", ", ".join(copied_files))

    return backup_dir


def cleanup_old_backups(keep: int) -> None:
    """يحتفظ بآخر (keep) نسخة احتياطية فقط، ويحذف الأقدم."""
    if not BACKUP_ROOT_DIR.exists():
        return

    backups = sorted(
        [d for d in BACKUP_ROOT_DIR.iterdir() if d.is_dir() and d.name.startswith("backup_")],
        key=lambda d: d.name,
        reverse=True,
    )

    old_backups = backups[keep:]
    for backup in old_backups:
        shutil.rmtree(backup)
        logger.info("تم حذف نسخة احتياطية قديمة: %s", backup.name)

    if not old_backups:
        logger.info("لا توجد نسخ قديمة تحتاج للحذف (الإجمالي: %d، الحد الأقصى: %d).", len(backups), keep)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="عمل نسخة احتياطية من فهرس FAISS")
    parser.add_argument(
        "--keep",
        type=int,
        default=None,
        help="عدد النسخ الاحتياطية المراد الاحتفاظ بها (الأقدم يتم حذفها تلقائياً)",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    logger.info("بدء عملية النسخ الاحتياطي لفهرس FAISS...")
    create_backup()

    if args.keep is not None:
        cleanup_old_backups(args.keep)

    logger.info("انتهت عملية النسخ الاحتياطي بنجاح.")


if __name__ == "__main__":
    main()
