# backend/app/database/docx_loader.py
"""
📝 تحميل النصوص من ملفات DOCX

يقرأ محتوى ملفات Word (.docx) ويستخرج النص منها
"""

import os
import re
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import zipfile
import xml.etree.ElementTree as ET
from datetime import datetime

from app.utils.logger import logger


class DocxLoader:
    """
    تحميل النصوص من ملفات DOCX
    
    يدعم:
    - استخراج النص من ملفات .docx
    - استخراج البيانات الوصفية
    - تنظيف النص المستخرج
    - قراءة الملفات في مجلدات
    """
    
    # مساحة أسماء XML في ملفات DOCX
    NAMESPACES = {
        'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main',
        'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships',
        'dc': 'http://purl.org/dc/elements/1.1/',
        'cp': 'http://schemas.openxmlformats.org/package/2006/metadata/core-properties',
        'dcterms': 'http://purl.org/dc/terms/'
    }
    
    def __init__(self, clean_text: bool = True, remove_extra_spaces: bool = True):
        """
        تهيئة أداة تحميل DOCX
        
        Args:
            clean_text: تنظيف النص من الرموز الزائدة
            remove_extra_spaces: إزالة المسافات الزائدة
        """
        self.clean_text = clean_text
        self.remove_extra_spaces = remove_extra_spaces
        
        # إحصائيات
        self.stats = {
            "total_loaded": 0,
            "total_failed": 0,
            "total_tokens": 0
        }
        
        logger.info("📝 DocxLoader initialized")
    
    # ============================================================
    # الطرق الرئيسية
    # ============================================================
    
    def load_file(self, file_path: str) -> Optional[Dict[str, Any]]:
        """
        تحميل ملف DOCX واحد
        
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
            
            if not path.suffix.lower() == '.docx':
                logger.warning(f"⚠️ Not a DOCX file: {file_path}")
                return None
            
            # استخراج النص
            text = self.extract_text(path)
            
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
            
            return {
                "text": text,
                "metadata": metadata,
                "file_path": str(path),
                "filename": path.name,
                "file_size": path.stat().st_size,
                "loaded_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Error loading DOCX {file_path}: {str(e)}")
            self.stats["total_failed"] += 1
            return None
    
    def load_directory(
        self,
        directory_path: str,
        recursive: bool = True,
        max_files: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        تحميل جميع ملفات DOCX في مجلد
        
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
        
        # البحث عن ملفات DOCX
        pattern = "**/*.docx" if recursive else "*.docx"
        files = list(path.glob(pattern))
        
        logger.info(f"📁 Found {len(files)} DOCX files in {directory_path}")
        
        # تحديد عدد الملفات
        if max_files and len(files) > max_files:
            files = files[:max_files]
            logger.info(f"📁 Limiting to {max_files} files")
        
        # تحميل كل ملف
        for file_path in files:
            doc = self.load_file(str(file_path))
            if doc:
                documents.append(doc)
        
        logger.info(f"✅ Loaded {len(documents)} DOCX documents")
        
        return documents
    
    # ============================================================
    # طرق استخراج النص
    # ============================================================
    
    def extract_text(self, file_path: Path) -> str:
        """
        استخراج النص من ملف DOCX
        
        Args:
            file_path: مسار الملف
            
        Returns:
            النص المستخرج
        """
        try:
            # فتح الملف كـ ZIP
            with zipfile.ZipFile(file_path, 'r') as zip_file:
                # قراءة ملف document.xml
                if 'word/document.xml' not in zip_file.namelist():
                    logger.warning(f"⚠️ No document.xml found in {file_path}")
                    return ""
                
                # قراءة المحتوى
                with zip_file.open('word/document.xml') as xml_file:
                    content = xml_file.read().decode('utf-8')
                    
                    # استخراج النص من XML
                    text = self._extract_text_from_xml(content)
                    
                    # إضافة النصوص من الرؤوس والتذييلات (اختياري)
                    text += self._extract_headers_and_footers(zip_file)
                    
                    # إضافة النصوص من الجداول
                    text += self._extract_tables(zip_file)
                    
                    return text
                    
        except Exception as e:
            logger.error(f"❌ Error extracting text from {file_path}: {str(e)}")
            return ""
    
    def _extract_text_from_xml(self, xml_content: str) -> str:
        """
        استخراج النص من محتوى XML
        
        Args:
            xml_content: محتوى XML
            
        Returns:
            النص المستخرج
        """
        try:
            # تحليل XML
            root = ET.fromstring(xml_content)
            
            # استخراج النص من جميع عناصر t
            texts = []
            for elem in root.iter():
                if elem.tag.endswith('t'):
                    if elem.text:
                        texts.append(elem.text)
                elif elem.tag.endswith('p'):  # فقرة جديدة
                    if texts and not texts[-1].endswith('\n'):
                        texts.append('\n')
            
            return ''.join(texts)
            
        except Exception as e:
            logger.error(f"❌ Error parsing XML: {str(e)}")
            return ""
    
    def _extract_headers_and_footers(self, zip_file: zipfile.ZipFile) -> str:
        """
        استخراج النص من الرؤوس والتذييلات
        
        Args:
            zip_file: ملف ZIP
            
        Returns:
            النص المستخرج من الرؤوس والتذييلات
        """
        text = ""
        
        # مسارات الرؤوس والتذييلات
        paths = [
            'word/header1.xml',
            'word/header2.xml',
            'word/header3.xml',
            'word/footer1.xml',
            'word/footer2.xml',
            'word/footer3.xml'
        ]
        
        for path in paths:
            if path in zip_file.namelist():
                try:
                    with zip_file.open(path) as f:
                        content = f.read().decode('utf-8')
                        extracted = self._extract_text_from_xml(content)
                        if extracted:
                            text += f"\n[{path}]\n{extracted}\n"
                except Exception as e:
                    continue
        
        return text
    
    def _extract_tables(self, zip_file: zipfile.ZipFile) -> str:
        """
        استخراج النص من الجداول
        
        Args:
            zip_file: ملف ZIP
            
        Returns:
            النص المستخرج من الجداول
        """
        text = ""
        
        if 'word/document.xml' in zip_file.namelist():
            try:
                with zip_file.open('word/document.xml') as f:
                    content = f.read().decode('utf-8')
                    root = ET.fromstring(content)
                    
                    # العثور على جميع الجداول
                    for table in root.iter():
                        if table.tag.endswith('tbl'):
                            text += "\n[TABLE]\n"
                            for row in table.iter():
                                if row.tag.endswith('tr'):
                                    row_text = []
                                    for cell in row.iter():
                                        if cell.tag.endswith('tc'):
                                            cell_text = self._extract_text_from_xml(
                                                ET.tostring(cell, encoding='unicode')
                                            )
                                            if cell_text.strip():
                                                row_text.append(cell_text.strip())
                                    if row_text:
                                        text += " | ".join(row_text) + "\n"
                            text += "[/TABLE]\n"
            except Exception as e:
                pass
        
        return text
    
    # ============================================================
    # طرق استخراج البيانات الوصفية
    # ============================================================
    
    def extract_metadata(self, file_path: Path) -> Dict[str, Any]:
        """
        استخراج البيانات الوصفية من ملف DOCX
        
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
            "modified_at": None,
            "author": None,
            "title": None,
            "subject": None,
            "keywords": None,
            "comments": None,
            "page_count": None,
            "word_count": None,
            "paragraph_count": None
        }
        
        try:
            # استخراج البيانات الوصفية من ملف DOCX
            with zipfile.ZipFile(file_path, 'r') as zip_file:
                # قراءة البيانات الوصفية من core.xml
                if 'docProps/core.xml' in zip_file.namelist():
                    with zip_file.open('docProps/core.xml') as f:
                        content = f.read().decode('utf-8')
                        metadata.update(self._extract_core_properties(content))
                
                # قراءة البيانات الوصفية من app.xml
                if 'docProps/app.xml' in zip_file.namelist():
                    with zip_file.open('docProps/app.xml') as f:
                        content = f.read().decode('utf-8')
                        metadata.update(self._extract_app_properties(content))
                        
        except Exception as e:
            logger.debug(f"⚠️ Could not extract metadata: {str(e)}")
        
        # إضافة تاريخ التحميل
        metadata["loaded_at"] = datetime.now().isoformat()
        
        return metadata
    
    def _extract_core_properties(self, content: str) -> Dict[str, Any]:
        """
        استخراج الخصائص الأساسية من core.xml
        
        Args:
            content: محتوى core.xml
            
        Returns:
            الخصائص الأساسية
        """
        properties = {}
        
        try:
            root = ET.fromstring(content)
            
            # استخراج العناصر الأساسية
            for child in root:
                tag = child.tag.split('}')[-1] if '}' in child.tag else child.tag
                
                if tag == 'title':
                    properties['title'] = child.text
                elif tag == 'subject':
                    properties['subject'] = child.text
                elif tag == 'creator':
                    properties['author'] = child.text
                elif tag == 'description':
                    properties['comments'] = child.text
                elif tag == 'keywords':
                    properties['keywords'] = child.text
                elif tag == 'created':
                    properties['created_at'] = child.text
                elif tag == 'modified':
                    properties['modified_at'] = child.text
                    
        except Exception as e:
            pass
        
        return properties
    
    def _extract_app_properties(self, content: str) -> Dict[str, Any]:
        """
        استخراج خصائص التطبيق من app.xml
        
        Args:
            content: محتوى app.xml
            
        Returns:
            خصائص التطبيق
        """
        properties = {}
        
        try:
            root = ET.fromstring(content)
            
            for child in root:
                tag = child.tag.split('}')[-1] if '}' in child.tag else child.tag
                
                if tag == 'Pages':
                    properties['page_count'] = int(child.text) if child.text else None
                elif tag == 'Words':
                    properties['word_count'] = int(child.text) if child.text else None
                elif tag == 'Paragraphs':
                    properties['paragraph_count'] = int(child.text) if child.text else None
                    
        except Exception as e:
            pass
        
        return properties
    
    def _guess_category(self, file_path: str) -> str:
        """
        تخمين تصنيف الملف من اسمه
        
        Args:
            file_path: مسار الملف
            
        Returns:
            التصنيف المخمن
        """
        filename = Path(file_path).name.lower()
        
        if 'contract' in filename or 'عقد' in filename:
            return 'contracts'
        elif 'policy' in filename or 'سياسة' in filename:
            return 'policies'
        elif 'quotation' in filename or 'عرض' in filename or 'سعر' in filename:
            return 'quotations'
        elif 'quality' in filename or 'جودة' in filename or 'تقرير' in filename:
            return 'quality_reports'
        elif 'report' in filename:
            return 'reports'
        elif 'manual' in filename or 'دليل' in filename:
            return 'manuals'
        elif 'invoice' in filename or 'فاتورة' in filename:
            return 'invoices'
        else:
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
        
        # إزالة علامات XML الزائدة
        text = re.sub(r'<[^>]+>', '', text)
        
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
            "total_tokens": self.stats["total_tokens"]
        }
    
    def reset_stats(self) -> None:
        """إعادة تعيين الإحصائيات"""
        self.stats = {
            "total_loaded": 0,
            "total_failed": 0,
            "total_tokens": 0
        }
        logger.info("🔄 DocxLoader stats reset")
    
    def is_supported(self, file_path: str) -> bool:
        """
        التحقق من أن الملف مدعوم
        
        Args:
            file_path: مسار الملف
            
        Returns:
            دعم الملف
        """
        return Path(file_path).suffix.lower() == '.docx'
    
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
        
        # محاولة استخراج البيانات الوصفية
        if info["is_supported"]:
            try:
                with zipfile.ZipFile(file_path, 'r') as zip_file:
                    if 'docProps/core.xml' in zip_file.namelist():
                        with zip_file.open('docProps/core.xml') as f:
                            content = f.read().decode('utf-8')
                            core = self._extract_core_properties(content)
                            info.update(core)
            except:
                pass
        
        return info
