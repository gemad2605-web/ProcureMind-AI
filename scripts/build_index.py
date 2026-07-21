"""
build_index.py
----------------
سكريبت لبناء فهرس FAISS من مستندات قاعدة المعرفة (knowledge_base).

المراحل:
    1. قراءة جميع ملفات DOCX من knowledge_base (السياسات، العقود، عروض الأسعار، تقارير الجودة)
    2. تقسيم النصوص إلى أجزاء (chunks)
    3. توليد المتجهات (embeddings) لكل جزء
    4. بناء فهرس FAISS وحفظه مع البيانات الوصفية

الاستخدام:
    python scripts/build_index.py
    python scripts/build_index.py --rebuild   # حذف الفهرس القديم وبناء فهرس جديد بالكامل
"""

import argparse
import json
import logging
import sys
from pathlib import Path

# إتاحة استيراد وحدات الـ backend من داخل السكريبت
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR / "backend"))

from app.database.docx_loader import load_docx_files  # noqa: E402
from app.database.embeddings import generate_embeddings  # noqa: E402
from app.database.faiss_loader import build_faiss_index, save_faiss_index  # noqa: E402
from app.rag.chunking import chunk_text  # noqa: E402
from app.utils.logger import get_logger  # noqa: E402

logger = get_logger("build_index") if "get_logger" in dir() else logging.getLogger("build_index")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

KNOWLEDGE_BASE_DIR = ROOT_DIR / "knowledge_base"
FAISS_INDEX_DIR = ROOT_DIR / "faiss_index"

KNOWLEDGE_SUBDIRS = ["policies", "contracts", "quotations", "quality_reports"]


def collect_documents() -> list[dict]:
    """يجمع كل ملفات DOCX من مجلدات قاعدة المعرفة الفرعية."""
    documents = []

    for subdir in KNOWLEDGE_SUBDIRS:
        folder_path = KNOWLEDGE_BASE_DIR / subdir
        if not folder_path.exists():
            logger.warning("المجلد غير موجود، تم تجاوزه: %s", folder_path)
            continue

        docx_files = sorted(folder_path.glob("*.docx"))
        logger.info("تم العثور على %d ملف في %s", len(docx_files), subdir)

        for file_path in docx_files:
            try:
                text = load_docx_files(str(file_path))
                documents.append(
                    {
                        "file_name": file_path.name,
                        "category": subdir,
                        "file_path": str(file_path.relative_to(ROOT_DIR)),
                        "text": text,
                    }
                )
            except Exception as exc:
                logger.error("فشل تحميل الملف %s: %s", file_path.name, exc)

    logger.info("إجمالي عدد المستندات التي تم تحميلها: %d", len(documents))
    return documents


def build_chunks(documents: list[dict]) -> tuple[list[str], list[dict]]:
    """يقسم كل مستند إلى أجزاء (chunks) ويحتفظ بالبيانات الوصفية لكل جزء."""
    all_chunks = []
    chunk_metadata = []

    for doc in documents:
        chunks = chunk_text(doc["text"])
        for i, chunk in enumerate(chunks):
            all_chunks.append(chunk)
            chunk_metadata.append(
                {
                    "file_name": doc["file_name"],
                    "category": doc["category"],
                    "file_path": doc["file_path"],
                    "chunk_index": i,
                }
            )

    logger.info("إجمالي عدد الأجزاء (chunks) الناتجة: %d", len(all_chunks))
    return all_chunks, chunk_metadata


def save_file_mapping(chunk_metadata: list[dict]) -> None:
    """يحفظ ملف ربط الأجزاء بالملفات الأصلية (file_mapping.json)."""
    mapping = {str(i): meta for i, meta in enumerate(chunk_metadata)}
    mapping_path = FAISS_INDEX_DIR / "file_mapping.json"

    with open(mapping_path, "w", encoding="utf-8") as f:
        json.dump(mapping, f, ensure_ascii=False, indent=2)

    logger.info("تم حفظ ملف الربط: %s", mapping_path)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="بناء فهرس FAISS من قاعدة المعرفة")
    parser.add_argument(
        "--rebuild",
        action="store_true",
        help="حذف الفهرس القديم بالكامل وبناء فهرس جديد من الصفر",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    FAISS_INDEX_DIR.mkdir(parents=True, exist_ok=True)

    if args.rebuild:
        logger.info("وضع إعادة البناء الكامل مفعّل — سيتم تجاهل أي فهرس سابق.")

    logger.info("بدء عملية بناء الفهرس...")

    documents = collect_documents()
    if not documents:
        logger.error("لم يتم العثور على أي مستندات في knowledge_base. تم إيقاف العملية.")
        sys.exit(1)

    chunks, chunk_metadata = build_chunks(documents)

    logger.info("جاري توليد المتجهات (embeddings)...")
    embeddings = generate_embeddings(chunks)

    logger.info("جاري بناء فهرس FAISS...")
    index = build_faiss_index(embeddings)

    save_faiss_index(index, str(FAISS_INDEX_DIR / "index.faiss"))
    save_file_mapping(chunk_metadata)

    index_config = {
        "total_documents": len(documents),
        "total_chunks": len(chunks),
        "categories": KNOWLEDGE_SUBDIRS,
    }
    with open(FAISS_INDEX_DIR / "index_config.json", "w", encoding="utf-8") as f:
        json.dump(index_config, f, ensure_ascii=False, indent=2)

    logger.info("تم بناء الفهرس بنجاح ✅")
    logger.info("عدد المستندات: %d | عدد الأجزاء: %d", len(documents), len(chunks))


if __name__ == "__main__":
    main()
