"""
load_texts.py
----------------
سكريبت لتحميل ومراجعة الملفات النصية (TXT) الناتجة من convert_docs.py
قبل إرسالها لعملية بناء الفهرس (build_index.py).

يقوم بـ:
    - تحميل جميع ملفات TXT من مجلد النصوص المحولة
    - التحقق من صحتها (ملفات فارغة، نصوص قصيرة جداً، ترميز غير صحيح)
    - عرض تقرير إحصائي عن حجم البيانات لكل تصنيف

الاستخدام:
    python scripts/load_texts.py
    python scripts/load_texts.py --source data/cache/converted_texts
    python scripts/load_texts.py --min-length 20
"""

import argparse
import logging
from pathlib import Path

# ============================================
# المسارات الأساسية
# ============================================
ROOT_DIR = Path(__file__).resolve().parent.parent
DEFAULT_SOURCE_DIR = ROOT_DIR / "data" / "cache" / "converted_texts"

# ============================================
# إعداد نظام التسجيل (Logging)
# ============================================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("load_texts")


def load_text_files(source_dir: Path, min_length: int) -> list[dict]:
    """
    يحمل كل ملفات TXT الموجودة في مجلد المصدر (متضمناً المجلدات الفرعية للتصنيفات).
    يرجع قائمة بالمستندات الصالحة فقط (بعد استبعاد الفارغة أو القصيرة جداً).
    """
    if not source_dir.exists():
        logger.error("مجلد المصدر غير موجود: %s", source_dir)
        logger.error("رجاء تشغيل scripts/convert_docs.py أولاً.")
        return []

    documents = []
    skipped = []

    txt_files = sorted(source_dir.rglob("*.txt"))
    logger.info("تم العثور على %d ملف نصي", len(txt_files))

    for file_path in txt_files:
        try:
            text = file_path.read_text(encoding="utf-8").strip()
        except UnicodeDecodeError:
            logger.warning("فشل قراءة الملف بترميز UTF-8، تم تجاوزه: %s", file_path.name)
            skipped.append(file_path.name)
            continue

        if len(text) < min_length:
            logger.warning(
                "الملف قصير جداً (%d حرف)، تم تجاوزه: %s", len(text), file_path.name
            )
            skipped.append(file_path.name)
            continue

        category = file_path.parent.name
        documents.append(
            {
                "file_name": file_path.name,
                "category": category,
                "file_path": str(file_path.relative_to(ROOT_DIR)),
                "text": text,
                "char_count": len(text),
            }
        )

    if skipped:
        logger.warning("إجمالي الملفات المتجاوزة: %d", len(skipped))

    return documents


def print_summary(documents: list[dict]) -> None:
    """يطبع تقرير إحصائي عن المستندات المحملة، مقسّم حسب التصنيف."""
    if not documents:
        logger.warning("لا توجد مستندات صالحة للعرض.")
        return

    categories = {}
    for doc in documents:
        categories.setdefault(doc["category"], {"count": 0, "chars": 0})
        categories[doc["category"]]["count"] += 1
        categories[doc["category"]]["chars"] += doc["char_count"]

    logger.info("=" * 50)
    logger.info("ملخص المستندات المحملة")
    logger.info("=" * 50)

    total_docs = 0
    total_chars = 0

    for category, stats in sorted(categories.items()):
        logger.info(
            "  %-20s | عدد الملفات: %-4d | إجمالي الأحرف: %d",
            category,
            stats["count"],
            stats["chars"],
        )
        total_docs += stats["count"]
        total_chars += stats["chars"]

    logger.info("-" * 50)
    logger.info("الإجمالي: %d مستند | %d حرف", total_docs, total_chars)
    logger.info("=" * 50)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="تحميل ومراجعة الملفات النصية قبل الفهرسة")
    parser.add_argument(
        "--source",
        type=str,
        default=None,
        help="مسار مجلد الملفات النصية (افتراضياً: data/cache/converted_texts)",
    )
    parser.add_argument(
        "--min-length",
        type=int,
        default=10,
        help="الحد الأدنى لعدد الأحرف لاعتبار الملف صالحاً (افتراضياً: 10)",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    source_dir = Path(args.source) if args.source else DEFAULT_SOURCE_DIR

    logger.info("بدء تحميل الملفات النصية من: %s", source_dir)

    documents = load_text_files(source_dir, args.min_length)
    print_summary(documents)


if __name__ == "__main__":
    main()
