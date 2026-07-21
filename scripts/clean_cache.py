"""
clean_cache.py
----------------
سكريبت لتنظيف ملفات التخزين المؤقت (cache) والملفات المؤقتة القديمة في مجلد data/.

الاستخدام:
    python scripts/clean_cache.py                # تنظيف مجلد cache بالكامل
    python scripts/clean_cache.py --older-than 7  # حذف الملفات الأقدم من 7 أيام فقط
    python scripts/clean_cache.py --dry-run       # عرض الملفات المرشحة للحذف بدون حذفها فعلياً
"""

import argparse
import logging
import shutil
import time
from pathlib import Path

# ============================================
# المسارات الأساسية
# ============================================
ROOT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT_DIR / "data"
CACHE_DIR = DATA_DIR / "cache"
UPLOADS_TMP_DIR = DATA_DIR / "uploads"

# ============================================
# إعداد نظام التسجيل (Logging)
# ============================================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("clean_cache")


def get_file_age_days(path: Path) -> float:
    """يحسب عمر الملف بالأيام بناءً على آخر تعديل عليه."""
    modified_time = path.stat().st_mtime
    age_seconds = time.time() - modified_time
    return age_seconds / 86400


def clean_directory(directory: Path, older_than: int | None, dry_run: bool) -> tuple[int, float]:
    """
    ينظف محتويات مجلد معين.
    older_than: لو محددة، يتم حذف الملفات الأقدم من العدد ده بالأيام فقط.
    يرجع عدد الملفات المحذوفة وإجمالي الحجم بالميجابايت.
    """
    if not directory.exists():
        logger.warning("المجلد غير موجود، تم تجاوزه: %s", directory)
        return 0, 0.0

    deleted_count = 0
    total_size_bytes = 0

    for item in directory.iterdir():
        # تجاهل ملفات .gitkeep عشان الهيكل يفضل موجود في Git
        if item.name == ".gitkeep":
            continue

        if older_than is not None:
            age_days = get_file_age_days(item)
            if age_days < older_than:
                continue

        try:
            size = item.stat().st_size if item.is_file() else sum(
                f.stat().st_size for f in item.rglob("*") if f.is_file()
            )

            if dry_run:
                logger.info("[تجربة فقط] سيتم حذف: %s (%.2f KB)", item.relative_to(ROOT_DIR), size / 1024)
            else:
                if item.is_file():
                    item.unlink()
                else:
                    shutil.rmtree(item)
                logger.info("تم حذف: %s (%.2f KB)", item.relative_to(ROOT_DIR), size / 1024)

            deleted_count += 1
            total_size_bytes += size

        except Exception as exc:
            logger.error("فشل حذف %s: %s", item, exc)

    return deleted_count, total_size_bytes / (1024 * 1024)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="تنظيف ملفات التخزين المؤقت")
    parser.add_argument(
        "--older-than",
        type=int,
        default=None,
        help="حذف الملفات الأقدم من عدد الأيام المحدد فقط (افتراضياً: حذف الكل)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="عرض الملفات المرشحة للحذف بدون حذفها فعلياً",
    )
    parser.add_argument(
        "--include-uploads",
        action="store_true",
        help="تضمين مجلد uploads المؤقت في عملية التنظيف",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if args.dry_run:
        logger.info("وضع التجربة فعّال — لن يتم حذف أي ملفات فعلياً.")

    logger.info("بدء تنظيف التخزين المؤقت...")

    total_deleted = 0
    total_size_mb = 0.0

    count, size_mb = clean_directory(CACHE_DIR, args.older_than, args.dry_run)
    total_deleted += count
    total_size_mb += size_mb

    if args.include_uploads:
        count, size_mb = clean_directory(UPLOADS_TMP_DIR, args.older_than, args.dry_run)
        total_deleted += count
        total_size_mb += size_mb

    action = "المرشحة للحذف" if args.dry_run else "المحذوفة"
    logger.info("انتهت العملية ✅ — عدد الملفات %s: %d | الحجم الإجمالي: %.2f MB", action, total_deleted, total_size_mb)


if __name__ == "__main__":
    main()
