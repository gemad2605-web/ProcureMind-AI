<div align="center">

<img src="https://capsule-render.vercel.app/api?type=waving&color=0:1e3a8a,100:2563eb&height=220&section=header&text=ProcureMind-AI&fontSize=60&fontColor=ffffff&animation=fadeIn&fontAlignY=38&desc=Smart%20Procurement%20Intelligence%20powered%20by%20RAG&descAlignY=58&descSize=20" width="100%"/>

<p>
نظام ذكاء اصطناعي متكامل لإدارة وتحليل بيانات المشتريات باستخدام تقنية <b>RAG (Retrieval-Augmented Generation)</b><br/>
يتيح البحث الذكي والتفاعل الطبيعي مع سياسات الشراء، العقود، عروض الأسعار، وتقارير الجودة
</p>

<p>
<img src="https://img.shields.io/badge/License-MIT-2563eb?style=for-the-badge" />
<img src="https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white" />
<img src="https://img.shields.io/badge/React-Frontend-61DAFB?style=for-the-badge&logo=react&logoColor=black" />
<img src="https://img.shields.io/badge/FastAPI-Backend-009688?style=for-the-badge&logo=fastapi&logoColor=white" />
<img src="https://img.shields.io/badge/FAISS-Vector%20DB-00A67E?style=for-the-badge" />
<img src="https://img.shields.io/badge/Docker-Ready-2496ED?style=for-the-badge&logo=docker&logoColor=white" />
</p>

<p>
<img src="https://img.shields.io/github/last-commit/gemad2605-web/ProcureMind-AI?style=flat-square&color=2563eb" />
<img src="https://img.shields.io/github/languages/top/gemad2605-web/ProcureMind-AI?style=flat-square&color=2563eb" />
<img src="https://img.shields.io/github/repo-size/gemad2605-web/ProcureMind-AI?style=flat-square&color=2563eb" />
</p>

</div>

---

## 📑 جدول المحتويات

- [نظرة عامة](#-نظرة-عامة)
- [المميزات الرئيسية](#-المميزات-الرئيسية)
- [البنية التقنية](#️-البنية-التقنية)
- [مخطط تدفق العمل](#-مخطط-تدفق-العمل)
- [لقطات من النظام](#-لقطات-من-النظام)
- [التشغيل السريع](#-التشغيل-السريع)
- [الاختبارات](#-الاختبارات)
- [التوثيق](#-التوثيق)
- [فريق العمل](#-فريق-العمل)
- [الترخيص](#️-الترخيص)

---

## 📋 نظرة عامة

**ProcureMind-AI** هو مساعد ذكي مبني على معمارية RAG، مصمم لمساعدة فرق المشتريات على الوصول الفوري للمعلومات من قاعدة معرفة ضخمة تشمل:

- 📜 **سياسات الشراء وتقييم الموردين**
- 📄 **العقود مع الموردين**
- 💰 **عروض الأسعار (Quotations)**
- ✅ **تقارير الجودة**

بدلاً من البحث اليدوي في عشرات الملفات، يمكن للمستخدم طرح سؤال بلغة طبيعية والحصول على إجابة دقيقة مدعومة بالمصادر الفعلية.

---

## ✨ المميزات الرئيسية

| الميزة | الوصف |
|---|---|
| 🔍 **بحث دلالي (Semantic Search)** | فهم معنى السؤال وليس فقط الكلمات المفتاحية |
| 🔄 **إعادة الترتيب (Reranking)** | تحسين دقة النتائج المسترجعة قبل توليد الإجابة |
| 🧩 **تقسيم ذكي للنصوص (Chunking)** | معالجة المستندات الطويلة بكفاءة |
| 💬 **واجهة محادثة تفاعلية** | مبنية بـ React لتجربة مستخدم سلسة |
| 📌 **عرض المصادر** | كل إجابة مرفقة بالمستند الذي استُخرجت منه |
| 🐳 **جاهز للنشر عبر Docker** | تشغيل موحّد للـ Backend والـ Frontend |
| ⚙️ **CI/CD تلقائي** | عبر GitHub Actions للاختبار والنشر |

---

## 🏗️ البنية التقنية

```
ProcureMind-AI/
├── backend/          # خادم FastAPI + محرك RAG
├── frontend/          # واجهة React
├── knowledge_base/   # قاعدة المعرفة (عقود، سياسات، عروض أسعار، تقارير جودة)
├── faiss_index/       # فهرس FAISS للبحث المتجهي
├── data/              # بيانات التشغيل (uploads, cache, logs, backups)
├── scripts/           # سكريبتات بناء وصيانة الفهرس
├── docs/               # التوثيق الفني الكامل
└── docker/            # إعدادات النشر
```

للتفاصيل الكاملة، راجع [Architecture.md](docs/Architecture.md).

---

## 🔄 مخطط تدفق العمل

```mermaid
flowchart LR
    A["👤 المستخدم"] --> B["💬 واجهة المحادثة<br/>React Frontend"]
    B --> C["⚡ FastAPI Backend"]
    C --> D["🔍 محرك RAG"]
    D --> E["📊 Semantic Search"]
    D --> F["🔄 Reranker"]
    E --> G["🗂️ فهرس FAISS"]
    F --> G
    G --> H["📚 قاعدة المعرفة<br/>عقود · سياسات · عروض أسعار · تقارير جودة"]
    D --> I["🧠 Groq LLM"]
    I --> C
    C --> B
    B --> A

    style A fill:#2563eb,color:#fff
    style I fill:#059669,color:#fff
    style H fill:#7c3aed,color:#fff
```

---

## 📸 لقطات من النظام

<div align="center">

| واجهة المحادثة | عرض المصادر | لوحة النتائج |
|:---:|:---:|:---:|
| <img src="docs/screenshots/chat.png" width="260"/> | <img src="docs/screenshots/sources.png" width="260"/> | <img src="docs/screenshots/dashboard.png" width="260"/> |

</div>

> 💡 ضع لقطات الشاشة الفعلية داخل `docs/screenshots/` بنفس الأسماء أعلاه ليتم عرضها تلقائيًا هنا.

---

## 🚀 التشغيل السريع

### المتطلبات الأساسية
- Python 3.10+
- Node.js 18+
- مفتاح Groq API ([احصل عليه من هنا](https://console.groq.com/keys))

### 1. استنساخ المشروع
```bash
git clone https://github.com/gemad2605-web/ProcureMind-AI.git
cd ProcureMind-AI
```

### 2. إعداد متغيرات البيئة
```bash
cp backend/.env.example backend/.env
```
ثم أضف مفتاح Groq API الخاص بك داخل `backend/.env`:
```
GROQ_API_KEY=your_groq_api_key_here
```

> ⚠️ **لا تشارك ملف `.env` أو مفتاحك مع أي شخص أو ترفعه على GitHub.**

### 3. تشغيل الـ Backend
```bash
cd backend
pip install -r requirements.txt
python main.py
```

### 4. تشغيل الـ Frontend
```bash
cd frontend
npm install
npm run dev
```

### أو باستخدام Docker
```bash
docker-compose -f docker/docker-compose.yml up
```

---

## 🧪 الاختبارات

```bash
cd backend
pytest tests/
```

---

## 📚 التوثيق

| المستند | الوصف |
|---|---|
| [API Documentation](docs/API_Documentation.md) | توثيق شامل لنقاط النهاية (Endpoints) |
| [Architecture](docs/Architecture.md) | شرح معماري النظام بالتفصيل |
| [Deployment Guide](docs/Deployment_Guide.md) | دليل خطوات النشر |
| [User Manual](docs/User_Manual.md) | دليل استخدام النظام للمستخدم النهائي |

---

## 👥 فريق العمل

<div align="center">
<table>
  <tr>
    <td align="center" width="200">
      <img src="https://api.dicebear.com/7.x/initials/svg?seed=Goda%20Emad&backgroundColor=2563eb" width="90" style="border-radius:50%"/><br/>
      <b>Goda Emad</b><br>
      <sub>🧠 Data Analyst & AI Developer</sub><br/>
      <a href="https://github.com/Goda-Emad"><img src="https://img.shields.io/badge/GitHub-181717?style=flat-square&logo=github&logoColor=white"/></a>
    </td>
    <td align="center" width="200">
      <img src="https://api.dicebear.com/7.x/initials/svg?seed=Gana%20Emad&backgroundColor=7c3aed" width="90" style="border-radius:50%"/><br/>
      <b>Gana Emad</b><br>
      <sub>👩‍💻 Team Member</sub>
    </td>
    <td align="center" width="200">
      <img src="https://api.dicebear.com/7.x/initials/svg?seed=Manar%20Harby&backgroundColor=059669" width="90" style="border-radius:50%"/><br/>
      <b>Manar Harby</b><br>
      <sub>👩‍💻 Team Member</sub>
    </td>
  </tr>
</table>
</div>

---

## 🛡️ الترخيص

هذا المشروع مرخّص بموجب [MIT License](LICENSE).

---

## 🤝 المساهمة

المساهمات مرحّب بها! يُرجى فتح Issue أو Pull Request لأي تحسينات أو إصلاحات.

---

<div align="center">
<img src="https://capsule-render.vercel.app/api?type=waving&color=0:2563eb,100:1e3a8a&height=100&section=footer" width="100%"/>
<p>صُنع بـ ❤️ لتحسين كفاءة إدارة المشتريات بالذكاء الاصطناعي</p>
</div>
