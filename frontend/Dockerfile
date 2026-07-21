# ============================================
# مرحلة البناء (Build Stage)
# ============================================
FROM node:20-alpine AS build

WORKDIR /app

# نسخ ملفات الحزم أولاً للاستفادة من Docker layer caching
COPY package*.json ./
RUN npm ci

# نسخ باقي الكود وبناء المشروع
COPY . .
RUN npm run build

# ============================================
# مرحلة التشغيل (Production Stage)
# ============================================
FROM nginx:1.27-alpine AS production

# نسخ ملفات الإعداد الخاصة بـ Nginx (اختياري - اعملي nginx.conf لو محتاجة SPA routing)
COPY --from=build /app/dist /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
