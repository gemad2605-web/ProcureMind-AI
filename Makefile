.PHONY: help install install-backend install-frontend dev dev-backend dev-frontend build build-index convert-docs load-texts backup-index clean-cache docker-up docker-down docker-build test lint

help:
	@echo "ProcureMind-AI — أوامر التشغيل السريعة"
	@echo ""
	@echo "  make install          تثبيت جميع الحزم (backend + frontend)"
	@echo "  make dev              تشغيل الـ backend والـ frontend معاً (وضع التطوير)"
	@echo "  make dev-backend      تشغيل الـ backend فقط"
	@echo "  make dev-frontend     تشغيل الـ frontend فقط"
	@echo "  make build            بناء الـ frontend للإنتاج"
	@echo "  make build-index      بناء فهرس FAISS من قاعدة المعرفة"
	@echo "  make convert-docs     تحويل ملفات DOCX إلى TXT"
	@echo "  make load-texts       مراجعة الملفات النصية قبل الفهرسة"
	@echo "  make backup-index     نسخ احتياطي لفهرس FAISS"
	@echo "  make clean-cache      تنظيف ملفات التخزين المؤقت"
	@echo "  make docker-up        تشغيل المشروع بالكامل عبر Docker"
	@echo "  make docker-down      إيقاف حاويات Docker"
	@echo "  make docker-build     إعادة بناء صور Docker"
	@echo "  make test             تشغيل اختبارات الـ backend"
	@echo "  make lint             فحص جودة كود الـ frontend"

# ============================================
# التثبيت
# ============================================
install: install-backend install-frontend

install-backend:
	cd backend && pip install -r requirements.txt --break-system-packages

install-frontend:
	cd frontend && npm install

# ============================================
# التشغيل (وضع التطوير)
# ============================================
dev-backend:
	cd backend && python -m app.main

dev-frontend:
	cd frontend && npm run dev

dev:
	@echo "شغّلي 'make dev-backend' و 'make dev-frontend' في تيرمينالين منفصلين"
	@echo "أو استخدمي 'make docker-up' لتشغيلهما معاً عبر Docker"

# ============================================
# البناء للإنتاج
# ============================================
build:
	cd frontend && npm run build

# ============================================
# سكريبتات قاعدة المعرفة والفهرسة
# ============================================
convert-docs:
	python scripts/convert_docs.py

load-texts:
	python scripts/load_texts.py

build-index:
	python scripts/build_index.py

backup-index:
	python scripts/backup_index.py --keep 5

clean-cache:
	python scripts/clean_cache.py

# ============================================
# Docker
# ============================================
docker-up:
	docker compose -f docker/docker-compose.yml up -d

docker-down:
	docker compose -f docker/docker-compose.yml down

docker-build:
	docker compose -f docker/docker-compose.yml build --no-cache

# ============================================
# الجودة والاختبارات
# ============================================
test:
	cd backend && pytest tests/ -v

lint:
	cd frontend && npm run lint
