# backend/app/database/text_loader.py
"""
📄 تحميل النصوص من ملفات TXT

يقرأ محتوى ملفات النص العادية (.txt) ويستخرج النص منها
"""

import os
import re
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import chardet

from app.utils.logger import logger


class TextLoader:
    """
    تحميل النصوص من ملفات TXT
    
    يدعم:
    - استخراج النص من ملفات .txt
    - استخراج البيانات الوصفية
    - تنظيف النص المستخرج
    - قراءة الملفات في مجلدات
    - التعرف على ترميز الملفات
    """
    
    def __init__(
        self,
        clean_text: bool = True,
        remove_extra_spaces: bool = True,
        detect_encoding: bool = True
    ):
        """
        تهيئة أداة تحميل النصوص
        
        Args:
            clean_text: تنظيف النص من الرموز الزائدة
            remove_extra_spaces: إزالة المسافات الزائدة
            detect_encoding: اكتشاف ترميز الملف تلقائياً
        """
        self.clean_text = clean_text
        self.remove_extra_spaces = remove_extra_spaces
        self.detect_encoding = detect_encoding
        
        # الترميزات المدعومة
        self.supported_encodings = ['utf-8', 'utf-16', 'windows-1256', 'iso-8859-1']
        
        # إحصائيات
        self.stats = {
            "total_loaded": 0,
            "total_failed": 0,
            "total_tokens": 0,
            "total_chars": 0
        }
        
        logger.info("📄 TextLoader initialized")
    
    # ============================================================
    # الطرق الرئيسية
    # ============================================================
    
    def load_file(self, file_path: str) -> Optional[Dict[str, Any]]:
        """
        تحميل ملف TXT واحد
        
        Args:
            file_path: مسار الملف
            
        Returns:
            بيانات الملف (نص + بيانات وصفية)
        """
        try:
            path = Path(file_path)
            
            if not path.exists():
                logger.error(f"❌ File not found: {file_path}")
                return None
            
            if not path.suffix.lower() == '.txt':
                logger.warning(f"⚠️ Not a TXT file: {file_path}")
                return None
            
            # قراءة النص مع اكتشاف الترميز
            text = self._read_file_with_encoding(path)
            
            if not text:
                logger.warning(f"⚠️ No text extracted from: {file_path}")
                return None
            
            # استخراج البيانات الوصفية
            metadata = self.extract_metadata(path)
            
            # تنظيف النص
            if self.clean_text:
                text = self._clean_extracted_text(text)
            
            # تحديث الإحصائيات
            self.stats["total_loaded"] += 1
            self.stats["total_tokens"] += len(text.split())
            self.stats["total_chars"] += len(text)
            
            return {
                "text": text,
                "metadata": metadata,
                "file_path": str(path),
                "filename": path.name,
                "file_size": path.stat().st_size,
                "loaded_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Error loading TXT {file_path}: {str(e)}")
            self.stats["total_failed"] += 1
            return None
    
    def load_directory(
        self,
        directory_path: str,
        recursive: bool = True,
        max_files: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        تحميل جميع ملفات TXT في مجلد
        
        Args:
            directory_path: مسار المجلد
            recursive: البحث في المجلدات الفرعية
            max_files: الحد الأقصى لعدد الملفات
            
        Returns:
            قائمة بيانات الملفات
        """
        documents = []
        path = Path(directory_path)
        
        if not path.exists():
            logger.error(f"❌ Directory not found: {directory_path}")
            return []
        
        # البحث عن ملفات TXT
        pattern = "**/*.txt" if recursive else "*.txt"
        files = list(path.glob(pattern))
        
        # استبعاد الملفات المخفية
        files = [f for f in files if not f.name.startswith('.')]
        
        logger.info(f"📁 Found {len(files)} TXT files in {directory_path}")
        
        # تحديد عدد الملفات
        if max_files and len(files) > max_files:
            files = files[:max_files]
            logger.info(f"📁 Limiting to {max_files} files")
        
        # تحميل كل ملف
        for file_path in files:
            doc = self.load_file(str(file_path))
            if doc:
                documents.append(doc)
        
        logger.info(f"✅ Loaded {len(documents)} TXT documents")
        
        return documents
    
    # ============================================================
    # طرق قراءة الملفات
    # ============================================================
    
    def _read_file_with_encoding(self, file_path: Path) -> str:
        """
        قراءة ملف مع اكتشاف الترميز
        
        Args:
            file_path: مسار الملف
            
        Returns:
            محتوى الملف
        """
        try:
            # محاولة القراءة بالترميزات المدعومة
            for encoding in self.supported_encodings:
                try:
                    with open(file_path, 'r', encoding=encoding) as f:
                        return f.read()
                except UnicodeDecodeError:
                    continue
            
            # إذا فشلت جميع المحاولات، استخدم اكتشاف الترميز
            if self.detect_encoding:
                try:
                    with open(file_path, 'rb') as f:
                        raw_data = f.read()
                        detected = chardet.detect(raw_data)
                        if detected and detected['encoding']:
                            return raw_data.decode(detected['encoding'])
                except Exception:
                    pass
            
            # آخر محاولة: قراءة مع تجاهل الأخطاء
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read()
                
        except Exception as e:
            logger.error(f"❌ Error reading file {file_path}: {str(e)}")
            return ""
    
    # ============================================================
    # طرق استخراج البيانات الوصفية
    # ============================================================
    
    def extract_metadata(self, file_path: Path) -> Dict[str, Any]:
        """
        استخراج البيانات الوصفية من الملف
        
        Args:
            file_path: مسار الملف
            
        Returns:
            البيانات الوصفية
        """
        metadata = {
            "filename": file_path.name,
            "file_path": str(file_path),
            "file_size": file_path.stat().st_size,
            "extension": file_path.suffix,
            "category": self._guess_category(str(file_path)),
            "created_at": None,
            "modified_at": None
        }
        
        # محاولة استخراج التاريخ من اسم الملف
        date_info = self._extract_date_from_filename(file_path.name)
        if date_info:
            metadata.update(date_info)
        
        # محاولة استخراج معلومات من محتوى الملف
        try:
            # قراءة أول 10 سطور للبحث عن معلومات
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = []
                for _ in range(10):
                    try:
                        line = f.readline()
                        if not line:
                            break
                        lines.append(line)
                    except:
                        break
                
                content_preview = ''.join(lines)
                
                # البحث عن معلومات في النص
                extracted = self._extract_info_from_content(content_preview)
                metadata.update(extracted)
                
        except Exception as e:
            logger.debug(f"⚠️ Could not extract metadata from content: {str(e)}")
        
        # إضافة تاريخ التحميل
        metadata["loaded_at"] = datetime.now().isoformat()
        
        return metadata
    
    def _extract_date_from_filename(self, filename: str) -> Dict[str, Any]:
        """
        استخراج التاريخ من اسم الملف
        
        Args:
            filename: اسم الملف
            
        Returns:
            معلومات التاريخ
        """
        info = {}
        
        # البحث عن تواريخ بصيغة YYYY-MM-DD
        date_patterns = [
            r'(\d{4})-(\d{2})-(\d{2})',  # 2024-01-15
            r'(\d{4})_(\d{2})_(\d{2})',  # 2024_01_15
            r'(\d{2})-(\d{2})-(\d{4})',  # 15-01-2024
            r'(\d{2})_(\d{2})_(\d{4})'   # 15_01_2024
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, filename)
            if match:
                try:
                    year, month, day = match.groups()
                    info["extracted_date"] = f"{year}-{month}-{day}"
                    info["extracted_year"] = int(year)
                    info["extracted_month"] = int(month)
                    info["extracted_day"] = int(day)
                    break
                except:
                    pass
        
        return info
    
    def _extract_info_from_content(self, content: str) -> Dict[str, Any]:
        """
        استخراج معلومات من محتوى النص
        
        Args:
            content: محتوى النص
            
        Returns:
            معلومات مستخرجة
        """
        info = {}
        
        # البحث عن عنوان
        title_patterns = [
            r'^(?:#|عنوان|Title|Subject)[:：\s]+(.+)$',
            r'^(.+)$'  # أول سطر غير فارغ
        ]
        
        lines = content.strip().split('\n')
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # محاولة استخراج العنوان
            for pattern in title_patterns:
                match = re.search(pattern, line, re.IGNORECASE)
                if match:
                    info["extracted_title"] = match.group(1).strip()
                    break
            
            if "extracted_title" in info:
                break
        
        # البحث عن كلمات مفتاحية
        keywords = []
        keyword_indicators = ['كلمات مفتاحية', 'keywords', 'tags', 'علامات']
        
        for indicator in keyword_indicators:
            for line in lines:
                if indicator.lower() in line.lower():
                    # استخراج الكلمات بعد المؤشر
                    parts = re.split(r'[:：\s]+', line, 1)
                    if len(parts) > 1:
                        keywords = [k.strip() for k in parts[1].split(',')]
                        break
            if keywords:
                break
        
        if keywords:
            info["extracted_keywords"] = keywords
        
        return info
    
    def _guess_category(self, file_path: str) -> str:
        """
        تخمين تصنيف الملف من اسمه ومساره
        
        Args:
            file_path: مسار الملف
            
        Returns:
            التصنيف المخمن
        """
        path = Path(file_path)
        filename = path.name.lower()
        parent = path.parent.name.lower()
        
        # الكلمات المفتاحية للتصنيفات
        category_keywords = {
            'contracts': ['contract', 'عقد', 'اتفاقية', 'agreement'],
            'policies': ['policy', 'سياسة', 'إجراء', 'procedure'],
            'quotations': ['quotation', 'عرض', 'سعر', 'quote', 'price'],
            'quality_reports': ['quality', 'جودة', 'تقرير', 'report', 'evaluation'],
            'invoices': ['invoice', 'فاتورة', 'bill', 'payment'],
            'purchase_orders': ['order', 'طلب', 'شراء', 'purchase', 'po'],
            'manuals': ['manual', 'دليل', 'guide', 'handbook'],
            'reports': ['report', 'تقرير', 'summary']
        }
        
        # البحث في اسم الملف
        for category, keywords in category_keywords.items():
            for keyword in keywords:
                if keyword in filename or keyword in parent:
                    return category
        
        # البحث في المسار الكامل
        path_str = str(path).lower()
        for category, keywords in category_keywords.items():
            for keyword in keywords:
                if keyword in path_str:
                    return category
        
        return 'other'
    
    # ============================================================
    # طرق تنظيف النص
    # ============================================================
    
    def _clean_extracted_text(self, text: str) -> str:
        """
        تنظيف النص المستخرج
        
        Args:
            text: النص الأصلي
            
        Returns:
            النص النظيف
        """
        if not text:
            return ""
        
        # إزالة الأحرف غير المرئية
        text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', text)
        
        # إزالة علامات XML/HTML
        text = re.sub(r'<[^>]+>', '', text)
        
        # إزالة الأحرف الخاصة المتكررة
        text = re.sub(r'[^\w\s\u0600-\u06FF\u0750-\u077F\uFB50-\uFDFF\uFE70-\uFEFF.,!?;:\-()"\' ]', '', text)
        
        # إزالة المسافات الزائدة
        if self.remove_extra_spaces:
            text = re.sub(r'\s+', ' ', text)
            text = re.sub(r'\n\s*\n', '\n\n', text)
        
        # إزالة الأسطر الفارغة المتعددة
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        # تنظيف بداية ونهاية النص
        text = text.strip()
        
        return text
    
    # ============================================================
    # طرق إضافية
    # ============================================================
    
    def load_texts_from_file(
        self,
        file_path: str,
        separator: str = "\n"
    ) -> List[str]:
        """
        تحميل نصوص متعددة من ملف واحد (مفصولة بفواصل)
        
        Args:
            file_path: مسار الملف
            separator: الفاصل بين النصوص
            
        Returns:
            قائمة النصوص
        """
        doc = self.load_file(file_path)
        if not doc:
            return []
        
        text = doc["text"]
        
        # تقسيم حسب الفاصل
        texts = text.split(separator)
        
        # تنظيف كل نص
        texts = [t.strip() for t in texts if t.strip()]
        
        return texts
    
    def load_by_pattern(
        self,
        directory_path: str,
        pattern: str = "*.txt",
        recursive: bool = True
    ) -> List[Dict[str, Any]]:
        """
        تحميل ملفات تطابق نمط معين
        
        Args:
            directory_path: مسار المجلد
            pattern: نمط الملفات
            recursive: البحث في المجلدات الفرعية
            
        Returns:
            قائمة بيانات الملفات
        """
        path = Path(directory_path)
        
        if not path.exists():
            logger.error(f"❌ Directory not found: {directory_path}")
            return []
        
        # البحث عن الملفات
        search_pattern = f"**/{pattern}" if recursive else pattern
        files = list(path.glob(search_pattern))
        
        documents = []
        for file_path in files:
            doc = self.load_file(str(file_path))
            if doc:
                documents.append(doc)
        
        return documents
    
    def get_stats(self) -> Dict[str, Any]:
        """
        الحصول على إحصائيات التحميل
        
        Returns:
            إحصائيات التحميل
        """
        return {
            **self.stats,
            "total_loaded": self.stats["total_loaded"],
            "total_failed": self.stats["total_failed"],
            "total_tokens": self.stats["total_tokens"],
            "total_chars": self.stats["total_chars"]
        }
    
    def reset_stats(self) -> None:
        """إعادة تعيين الإحصائيات"""
        self.stats = {
            "total_loaded": 0,
            "total_failed": 0,
            "total_tokens": 0,
            "total_chars": 0
        }
        logger.info("🔄 TextLoader stats reset")
    
    def is_supported(self, file_path: str) -> bool:
        """
        التحقق من أن الملف مدعوم
        
        Args:
            file_path: مسار الملف
            
        Returns:
            دعم الملف
        """
        return Path(file_path).suffix.lower() == '.txt'
    
    def get_file_info(self, file_path: str) -> Dict[str, Any]:
        """
        الحصول على معلومات الملف بدون تحميله بالكامل
        
        Args:
            file_path: مسار الملف
            
        Returns:
            معلومات الملف
        """
        path = Path(file_path)
        
        info = {
            "filename": path.name,
            "file_path": str(path),
            "file_size": path.stat().st_size,
            "extension": path.suffix,
            "is_supported": self.is_supported(file_path),
            "category": self._guess_category(file_path)
        }
        
        # محاولة قراءة أول 500 حرف لتخمين المحتوى
        try:
            content = self._read_file_with_encoding(path)
            if content:
                preview = content[:500]
                info["preview"] = preview
                info["line_count"] = len(content.split('\n'))
                info["word_count"] = len(content.split())
        except:
            pass
        
        return info
