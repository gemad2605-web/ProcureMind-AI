ProcureMind-AI/
│
├── 📁 .github/                                    # إعدادات GitHub
│   └── 📁 workflows/                              # GitHub Actions
│       ├── deploy.yml                             # نشر تلقائي
│       └── test.yml                               # اختبار تلقائي
│
├── 📁 backend/                                    # خادم التطبيق
│   │
│   ├── 📁 app/                                    # التطبيق الأساسي
│   │   │
│   │   ├── 📁 api/                                # طبقة الـ API
│   │   │   ├── __init__.py
│   │   │   ├── routes.py                          # تسجيل جميع المسارات
│   │   │   ├── chat.py                            # نقطة نهاية المحادثة
│   │   │   ├── health.py                          # التحقق من الصحة
│   │   │   └── documents.py                       # إدارة المستندات
│   │   │
│   │   ├── 📁 rag/                                # محرك RAG
│   │   │   ├── __init__.py
│   │   │   ├── retriever.py                       # استرجاع النصوص
│   │   │   ├── semantic_search.py                 # البحث الدلالي
│   │   │   ├── qa_engine.py                       # محرك الأسئلة
│   │   │   ├── reranker.py                        # إعادة ترتيب النتائج
│   │   │   └── chunking.py                        # تقسيم النصوص
│   │   │
│   │   ├── 📁 llm/                                # طبقة النماذج اللغوية
│   │   │   ├── __init__.py
│   │   │   ├── grok_client.py                     # عميل Grok
│   │   │   └── llm_factory.py                     # مصنع النماذج
│   │   │
│   │   ├── 📁 database/                           # طبقة قواعد البيانات
│   │   │   ├── __init__.py
│   │   │   ├── faiss_loader.py                    # تحميل FAISS
│   │   │   ├── embeddings.py                      # توليد المتجهات
│   │   │   ├── text_loader.py                     # تحميل النصوص
│   │   │   ├── docx_loader.py                     # تحميل DOCX
│   │   │   └── file_mapper.py                     # ربط الملفات
│   │   │
│   │   ├── 📁 models/                             # نماذج البيانات
│   │   │   ├── __init__.py
│   │   │   └── schemas.py                         # نماذج Pydantic
│   │   │
│   │   ├── 📁 core/                               # الإعدادات الأساسية
│   │   │   ├── __init__.py
│   │   │   ├── config.py                          # إعدادات التطبيق
│   │   │   └── prompts.py                         # قوالب الأسئلة
│   │   │
│   │   ├── 📁 services/                           # طبقة الخدمات
│   │   │   ├── __init__.py
│   │   │   └── chat_service.py                    # خدمة المحادثة
│   │   │
│   │   ├── 📁 utils/                              # أدوات مساعدة
│   │   │   ├── __init__.py
│   │   │   ├── logger.py                          # نظام التسجيل
│   │   │   └── file_utils.py                      # التعامل مع الملفات
│   │   │
│   │   └── 📄 main.py                             # نقطة الدخول الرئيسية
│   │
│   ├── 📁 tests/                                  # اختبارات التطبيق
│   │   ├── __init__.py
│   │   ├── test_chat.py                           # اختبار المحادثة
│   │   └── test_rag.py                            # اختبار RAG
│   │
│   ├── 📄 requirements.txt                        # حزم Python
│   ├── 📄 Dockerfile                              # صورة Docker
│   └── 📄 .env.example                            # نموذج المتغيرات البيئية
│
├── 📁 frontend/                                   # واجهة المستخدم
│   │
│   ├── 📁 public/                                 # ملفات عامة
│   │   ├── logo.png                               # شعار التطبيق
│   │   └── favicon.ico                            # أيقونة المتصفح
│   │
│   ├── 📁 src/                                    # كود المصدر
│   │   │
│   │   ├── 📁 api/                                # الاتصال بالـ Backend
│   │   │   ├── procuremind.js                     # عميل API
│   │   │   └── endpoints.js                       # نقاط النهاية
│   │   │
│   │   ├── 📁 components/                         # المكونات
│   │   │   │
│   │   │   ├── 📁 layout/                         # مكونات التخطيط
│   │   │   │   ├── Navbar.jsx                     # شريط التنقل
│   │   │   │   └── Footer.jsx                     # التذييل
│   │   │   │
│   │   │   ├── 📁 chat/                           # مكونات المحادثة
│   │   │   │   ├── ChatContainer.jsx              # حاوية المحادثة
│   │   │   │   ├── MessageList.jsx                # قائمة الرسائل
│   │   │   │   ├── Message.jsx                    # عرض رسالة
│   │   │   │   ├── ChatInput.jsx                  # مدخل النص
│   │   │   │   ├── Sources.jsx                    # عرض المصادر
│   │   │   │   └── SuggestedQuestions.jsx         # أسئلة مقترحة
│   │   │   │
│   │   │   └── 📁 common/                         # مكونات عامة
│   │   │       ├── Loading.jsx                    # مؤشر التحميل
│   │   │       └── EmptyState.jsx                 # حالة فارغة
│   │   │
│   │   ├── 📁 pages/                              # الصفحات
│   │   │   └── Home.jsx                           # الصفحة الرئيسية
│   │   │
│   │   ├── 📁 hooks/                              # خطافات React
│   │   │   └── useChat.js                         # إدارة المحادثة
│   │   │
│   │   ├── 📁 context/                            # سياقات React
│   │   │   └── ChatContext.jsx                    # سياق المحادثة
│   │   │
│   │   ├── 📁 styles/                             # أنماط CSS
│   │   │   └── globals.css                        # أنماط عامة
│   │   │
│   │   ├── 📄 App.jsx                             # المكون الرئيسي
│   │   └── 📄 main.jsx                            # نقطة الدخول
│   │
│   ├── 📄 package.json                            # حزم Node.js
│   ├── 📄 vite.config.js                          # إعدادات Vite
│   ├── 📄 Dockerfile                              # صورة Docker
│   └── 📄 index.html                              # الصفحة الرئيسية
│
├── 📁 knowledge_base/                             # 📌 قاعدة المعرفة
│   │
│   ├── 📁 policies/                               # السياسات
│   │   ├── 01_Procurement_Policy.docx
│   │   └── 02_Supplier_Evaluation_Policy.docx
│   │
│   ├── 📁 contracts/                              # العقود
│   │   ├── 03_Supplier_Contract_Alpha_Inc.docx
│   │   ├── 04_Supplier_Contract_Beta_Supplies.docx
│   │   ├── 05_Supplier_Contract_Delta_Logistics.docx
│   │   ├── 06_Supplier_Contract_Epsilon_Group.docx
│   │   └── 07_Supplier_Contract_Gamma_Co.docx
│   │
│   ├── 📁 quotations/                             # عروض الأسعار
│   │   ├── 08_Quotation_Alpha_Inc.docx
│   │   ├── 09_Quotation_Beta_Supplies.docx
│   │   ├── 10_Quotation_Delta_Logistics.docx
│   │   ├── 11_Quotation_Epsilon_Group.docx
│   │   └── 13_Quotation_Gamma_Co.docx
│   │
│   ├── 📁 quality_reports/                        # تقارير الجودة
│   │   ├── 13_Quality_Report_Alpha_Inc.docx
│   │   ├── 14_Quality_Report_Beta_Supplies.docx
│   │   ├── 15_Quality_Report_Delta_Logistics.docx
│   │   ├── 16_Quality_Report_Epsilon_Group.docx
│   │   └── 17_Quality_Report_Gamma_Co.docx
│   │
│   └── 📁 metadata/                               # بيانات وصفية
│       ├── file_index.json                        # فهرس الملفات
│       ├── categories.json                        # التصنيفات
│       └── supplier_info.json                     # معلومات الموردين
│
├── 📁 data/                                       # 📌 بيانات التطبيق المحلية
│   ├── 📁 uploads/                                # الملفات المرفوعة
│   ├── 📁 cache/                                  # التخزين المؤقت
│   ├── 📁 exports/                                # الملفات المصدرة
│   ├── 📁 logs/                                   # سجلات التطبيق
│   │   ├── app.log
│   │   └── error.log
│   └── 📁 backups/                                # النسخ الاحتياطية
│       └── faiss_backup/
│
├── 📁 faiss_index/                                # 📌 فهرس FAISS
│   ├── index.faiss                                # ملف الفهرس الثنائي
│   ├── metadata.pkl                               # البيانات الوصفية
│   ├── file_mapping.json                          # ربط الملفات بالفهرس
│   └── index_config.json                          # إعدادات الفهرس
│
├── 📁 scripts/                                    # 📌 سكريبتات التشغيل
│   ├── build_index.py                             # بناء الفهرس
│   ├── load_texts.py                              # تحميل النصوص
│   ├── convert_docs.py                            # تحويل DOCX إلى TXT
│   ├── backup_index.py                            # نسخ احتياطي للفهرس
│   └── clean_cache.py                             # تنظيف التخزين المؤقت
│
├── 📁 docs/                                       # 📌 وثائق المشروع
│   ├── API_Documentation.md                       # توثيق API
│   ├── Architecture.md                            # معمارية النظام
│   ├── Deployment_Guide.md                        # دليل النشر
│   └── User_Manual.md                             # دليل المستخدم
│
├── 📁 docker/                                     # 📌 إعدادات Docker
│   ├── docker-compose.yml                         # تشغيل جميع الخدمات
│   └── docker-compose.dev.yml                     # للتطوير
│
├── 📄 .gitignore                                  # ملفات مستبعدة من Git
├── 📄 README.md                                   # وصف المشروع
├── 📄 LICENSE                                     # رخصة المشروع
├── 📄 Makefile                                    # أوامر التشغيل السريعة
├── 📄 start.py                                    # 🚀 تشغيل المشروع
├── 📄 .env                                        # المتغيرات البيئية
└── 📄 .env.example                                # نموذج المتغيرات البيئية