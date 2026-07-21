"""
start.py
----------------
نقطة التشغيل الرئيسية لمشروع ProcureMind-AI.

يقوم بـ:
    1. التحقق من وجود ملف .env
    2. التحقق من وجود فهرس FAISS (وتنبيه المستخدم لو مش موجود)
    3. تشغيل خادم الـ backend (FastAPI عبر uvicorn)

الاستخدام:
    python start.py
    python start.py --port 8080
    python start.py --skip-checks   # تخطي التحقق من .env والفهرس
"""

import argparse
import logging
import subprocess
import sys
from pathlib import Path

# ============================================
# المسارات الأساسية
# ============================================
ROOT_DIR = Path(__file__).resolve().parent
BACKEND_DIR = ROOT_DIR / "backend"
ENV_FILE = ROOT_DIR / ".env"
FAISS_INDEX_FILE = ROOT_DIR / "faiss_index" / "index.faiss"

# ============================================
# إعداد نظام التسجيل (Logging)
# ============================================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("start")


def check_env_file() -> bool:
    """يتحقق من وجود ملف .env قبل التشغيل."""
    if not ENV_FILE.exists():
        logger.error("ملف .env غير موجود في جذر المشروع.")
        logger.error("قومي بإنشائه أولاً: cp .env.example .env")
        return False

    logger.info("تم التحقق من ملف .env بنجاح ✅")
    return True


def check_faiss_index() -> bool:
    """يتحقق من وجود فهرس FAISS، وينبه المستخدم لو غير موجود (بدون إيقاف التشغيل)."""
    if not FAISS_INDEX_FILE.exists():
        logger.warning("فهرس FAISS غير موجود بعد.")
        logger.warning("سيعمل الخادم لكن ميزة البحث عن المستندات لن تعمل حتى تقومي بتشغيل:")
        logger.warning("    python scripts/build_index.py")
        return False

    logger.info("تم التحقق من وجود فهرس FAISS بنجاح ✅")
    return True


def run_backend(port: int) -> None:
    """يشغّل خادم FastAPI عبر uvicorn."""
    logger.info("جاري تشغيل خادم ProcureMind-AI على المنفذ %d ...", port)

    command = [
        sys.executable,
        "-m",
        "uvicorn",
        "app.main:app",
        "--reload",
        "--host",
        "0.0.0.0",
        "--port",
        str(port),
    ]

    try:
        subprocess.run(command, cwd=str(BACKEND_DIR), check=True)
    except FileNotFoundError:
        logger.error("لم يتم العثور على uvicorn. رجاء تثبيت المتطلبات أولاً:")
        logger.error("    pip install -r backend/requirements.txt")
        sys.exit(1)
    except subprocess.CalledProcessError as exc:
        logger.error("فشل تشغيل الخادم: %s", exc)
        sys.exit(1)
    except KeyboardInterrupt:
        logger.info("تم إيقاف الخادم بواسطة المستخدم.")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="تشغيل مشروع ProcureMind-AI")
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="المنفذ الذي سيعمل عليه الخادم (افتراضياً: 8000)",
    )
    parser.add_argument(
        "--skip-checks",
        action="store_true",
        help="تخطي التحقق من .env وفهرس FAISS قبل التشغيل",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    logger.info("🚀 بدء تشغيل ProcureMind-AI")

    if not args.skip_checks:
        env_ok = check_env_file()
        if not env_ok:
            sys.exit(1)
        check_faiss_index()  # تحذير فقط، لا يوقف التشغيل

    run_backend(args.port)


if __name__ == "__main__":
    main()
