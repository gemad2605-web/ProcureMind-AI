# backend/Dockerfile
# 🐳 Dockerfile لبناء صورة Backend لتطبيق ProcureMind-AI

# ============================================================
# 1. مرحلة البناء (Build Stage)
# ============================================================

# استخدام صورة Python الرسمية
FROM python:3.10-slim AS builder

# تثبيت الأدوات اللازمة للبناء
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# تعيين دليل العمل
WORKDIR /app

# نسخ ملفات المتطلبات أولاً (للاستفادة من التخزين المؤقت)
COPY requirements.txt .

# تثبيت التبعيات
RUN pip install --no-cache-dir -r requirements.txt

# ============================================================
# 2. المرحلة النهائية (Final Stage)
# ============================================================

FROM python:3.10-slim

# تثبيت الأدوات الأساسية
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# إنشاء مستخدم غير جذر للتشغيل
RUN groupadd -r procuremind && useradd -r -g procuremind procuremind

# تعيين دليل العمل
WORKDIR /app

# نسخ التبعيات من مرحلة البناء
COPY --from=builder /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# نسخ كود التطبيق
COPY . .

# تغيير مالك الملفات للمستخدم الجديد
RUN chown -R procuremind:procuremind /app

# التبديل إلى المستخدم غير الجذر
USER procuremind

# ============================================================
# 3. إعدادات البيئة
# ============================================================

# متغيرات البيئة الافتراضية
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV ENVIRONMENT=production
ENV DEBUG=False

# ============================================================
# 4. المنافذ والصحة
# ============================================================

# كشف المنفذ
EXPOSE 8000

# إعدادات فحص الصحة (Health Check)
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/health || exit 1

# ============================================================
# 5. تشغيل التطبيق
# ============================================================

# تشغيل التطبيق باستخدام Uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
