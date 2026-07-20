# backend/app/database/file_mapper.py
"""
🗺️ ربط الملفات بالفهارس والبيانات الوصفية

يقوم بإدارة العلاقة بين الملفات وفهارس FAISS والبيانات الوصفية
"""

import json
import hashlib
from pathlib import Path
from typing import List, Dict, Any, Optional, Set
from datetime import datetime
import pickle

from app.core.config import settings
from app.utils.logger import logger


class FileMapper:
    """
    إدارة ربط الملفات بالفهارس
    
    يدعم:
    - تتبع الملفات المضافة
    - تحديث الفهرس عند إضافة ملفات جديدة
    - التحقق من تغييرات الملفات
    - إدارة الإصدارات
    """
    
    def __init__(
        self,
        mapping_file: Optional[str] = None,
        index_path: Optional[str] = None
    ):
        """
        تهيئة أداة ربط الملفات
        
        Args:
            mapping_file: مسار ملف التعيين
            index_path: مسار الفهرس
        """
        self.mapping_file = Path(mapping_file or settings.FAISS_INDEX_PATH / "file_mapping.json")
        self.index_path = Path(index_path or settings.FAISS_INDEX_PATH)
        
        # تحميل التعيينات
        self.mappings = {}
        self.file_hashes = {}
        self.category_counts = {}
        
        # تحميل البيانات
        self.load()
        
        logger.info("🗺️ FileMapper initialized")
    
    # ============================================================
    # طرق التحميل والحفظ
    # ============================================================
    
    def load(self) -> bool:
        """
        تحميل التعيينات من ملف JSON
        
        Returns:
            نجاح التحميل
        """
        try:
            if self.mapping_file.exists():
                with open(self.mapping_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.mappings = data.get("mappings", {})
                    self.file_hashes = data.get("file_hashes", {})
                    self.category_counts = data.get("category_counts", {})
                
                logger.info(f"✅ File mappings loaded: {len(self.mappings)} files")
                return True
            else:
                logger.info("📁 No existing mapping file, creating new")
                self.mappings = {}
                self.file_hashes = {}
                self.category_counts = {}
                return True
                
        except Exception as e:
            logger.error(f"❌ Error loading mappings: {str(e)}")
            self.mappings = {}
            self.file_hashes = {}
            self.category_counts = {}
            return False
    
    def save(self) -> bool:
        """
        حفظ التعيينات إلى ملف JSON
        
        Returns:
            نجاح الحفظ
        """
        try:
            # إنشاء المجلد إذا لم يكن موجوداً
            self.mapping_file.parent.mkdir(parents=True, exist_ok=True)
            
            data = {
                "mappings": self.mappings,
                "file_hashes": self.file_hashes,
                "category_counts": self.category_counts,
                "last_updated": datetime.now().isoformat(),
                "total_files": len(self.mappings),
                "version": "1.0"
            }
            
            with open(self.mapping_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"✅ File mappings saved: {len(self.mappings)} files")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error saving mappings: {str(e)}")
            return False
    
    # ============================================================
    # طرق إدارة الملفات
    # ============================================================
    
    def add_file(
        self,
        file_path: str,
        doc_id: str,
        category: str,
        metadata: Dict[str, Any]
    ) -> bool:
        """
        إضافة ملف إلى التعيينات
        
        Args:
            file_path: مسار الملف
            doc_id: معرف المستند
            category: تصنيف الملف
            metadata: البيانات الوصفية
            
        Returns:
            نجاح الإضافة
        """
        try:
            path = Path(file_path)
            
            # حساب Hash الملف
            file_hash = self._calculate_file_hash(path)
            
            # تخزين التعيين
            self.mappings[doc_id] = {
                "file_path": str(path),
                "filename": path.name,
                "category": category,
                "metadata": metadata,
                "added_at": datetime.now().isoformat(),
                "file_hash": file_hash,
                "file_size": path.stat().st_size
            }
            
            # تخزين Hash
            self.file_hashes[str(path)] = file_hash
            
            # تحديث عدد التصنيفات
            if category not in self.category_counts:
                self.category_counts[category] = 0
            self.category_counts[category] += 1
            
            logger.info(f"✅ File added: {path.name} -> {doc_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error adding file: {str(e)}")
            return False
    
    def remove_file(self, doc_id: str) -> bool:
        """
        حذف ملف من التعيينات
        
        Args:
            doc_id: معرف المستند
            
        Returns:
            نجاح الحذف
        """
        try:
            if doc_id not in self.mappings:
                logger.warning(f"⚠️ Document not found: {doc_id}")
                return False
            
            # الحصول على التصنيف
            category = self.mappings[doc_id].get("category")
            
            # حذف من التعيينات
            del self.mappings[doc_id]
            
            # تحديث عدد التصنيفات
            if category and category in self.category_counts:
                self.category_counts[category] -= 1
                if self.category_counts[category] <= 0:
                    del self.category_counts[category]
            
            logger.info(f"✅ File removed: {doc_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error removing file: {str(e)}")
            return False
    
    def update_file(
        self,
        doc_id: str,
        file_path: str,
        metadata: Dict[str, Any]
    ) -> bool:
        """
        تحديث ملف في التعيينات
        
        Args:
            doc_id: معرف المستند
            file_path: مسار الملف الجديد
            metadata: البيانات الوصفية الجديدة
            
        Returns:
            نجاح التحديث
        """
        try:
            if doc_id not in self.mappings:
                logger.warning(f"⚠️ Document not found: {doc_id}")
                return False
            
            path = Path(file_path)
            
            # حساب Hash الملف الجديد
            file_hash = self._calculate_file_hash(path)
            
            # تحديث التعيين
            self.mappings[doc_id].update({
                "file_path": str(path),
                "filename": path.name,
                "metadata": metadata,
                "updated_at": datetime.now().isoformat(),
                "file_hash": file_hash,
                "file_size": path.stat().st_size
            })
            
            # تحديث Hash
            self.file_hashes[str(path)] = file_hash
            
            logger.info(f"✅ File updated: {doc_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error updating file: {str(e)}")
            return False
    
    # ============================================================
    # طرق البحث والاستعلام
    # ============================================================
    
    def get_document(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """
        الحصول على معلومات مستند
        
        Args:
            doc_id: معرف المستند
            
        Returns:
            معلومات المستند أو None
        """
        return self.mappings.get(doc_id)
    
    def get_documents_by_category(self, category: str) -> List[Dict[str, Any]]:
        """
        الحصول على جميع المستندات في تصنيف
        
        Args:
            category: التصنيف
            
        Returns:
            قائمة المستندات
        """
        return [
            {"id": doc_id, **info}
            for doc_id, info in self.mappings.items()
            if info.get("category") == category
        ]
    
    def get_documents_by_file_path(self, file_path: str) -> Optional[Dict[str, Any]]:
        """
        الحصول على مستند بواسطة مساره
        
        Args:
            file_path: مسار الملف
            
        Returns:
            المستند أو None
        """
        for doc_id, info in self.mappings.items():
            if info.get("file_path") == file_path:
                return {"id": doc_id, **info}
        return None
    
    def get_all_documents(self) -> List[Dict[str, Any]]:
        """
        الحصول على جميع المستندات
        
        Returns:
            قائمة جميع المستندات
        """
        return [
            {"id": doc_id, **info}
            for doc_id, info in self.mappings.items()
        ]
    
    def get_categories(self) -> Dict[str, int]:
        """
        الحصول على التصنيفات مع عدد المستندات
        
        Returns:
            التصنيفات مع العدد
        """
        return self.category_counts.copy()
    
    def get_total_files(self) -> int:
        """
        الحصول على عدد الملفات
        
        Returns:
            عدد الملفات
        """
        return len(self.mappings)
    
    # ============================================================
    # طرق التحقق
    # ============================================================
    
    def is_file_indexed(self, file_path: str) -> bool:
        """
        التحقق من أن الملف مفهرس
        
        Args:
            file_path: مسار الملف
            
        Returns:
            هل الملف مفهرس
        """
        return str(file_path) in self.file_hashes
    
    def has_file_changed(self, file_path: str) -> bool:
        """
        التحقق من تغير الملف
        
        Args:
            file_path: مسار الملف
            
        Returns:
            هل تغير الملف
        """
        path = Path(file_path)
        if not path.exists():
            return True
        
        current_hash = self._calculate_file_hash(path)
        stored_hash = self.file_hashes.get(str(path))
        
        return current_hash != stored_hash
    
    def get_missing_files(self) -> List[str]:
        """
        الحصول على الملفات المفقودة (غير الموجودة فعلياً)
        
        Returns:
            قائمة الملفات المفقودة
        """
        missing = []
        for doc_id, info in self.mappings.items():
            file_path = Path(info.get("file_path", ""))
            if not file_path.exists():
                missing.append(doc_id)
        return missing
    
    def get_changed_files(self) -> List[str]:
        """
        الحصول على الملفات المتغيرة
        
        Returns:
            قائمة الملفات المتغيرة
        """
        changed = []
        for doc_id, info in self.mappings.items():
            file_path = info.get("file_path", "")
            if self.has_file_changed(file_path):
                changed.append(doc_id)
        return changed
    
    # ============================================================
    # طرق الإحصائيات
    # ============================================================
    
    def get_stats(self) -> Dict[str, Any]:
        """
        الحصول على إحصائيات التعيينات
        
        Returns:
            إحصائيات التعيينات
        """
        missing = self.get_missing_files()
        changed = self.get_changed_files()
        
        return {
            "total_files": self.get_total_files(),
            "categories": self.category_counts,
            "categories_count": len(self.category_counts),
            "missing_files": len(missing),
            "changed_files": len(changed),
            "last_updated": datetime.now().isoformat()
        }
    
    # ============================================================
    # طرق مساعدة
    # ============================================================
    
    def _calculate_file_hash(self, file_path: Path) -> str:
        """
        حساب Hash للملف
        
        Args:
            file_path: مسار الملف
            
        Returns:
            Hash الملف
        """
        try:
            if not file_path.exists():
                return ""
            
            # استخدام حجم الملف + اسم الملف + تاريخ التعديل
            stat = file_path.stat()
            content = f"{file_path.name}_{stat.st_size}_{stat.st_mtime}"
            return hashlib.md5(content.encode()).hexdigest()
            
        except Exception as e:
            logger.error(f"❌ Error calculating hash: {str(e)}")
            return ""
    
    def _calculate_file_content_hash(self, file_path: Path) -> str:
        """
        حساب Hash لمحتوى الملف
        
        Args:
            file_path: مسار الملف
            
        Returns:
            Hash المحتوى
        """
        try:
            if not file_path.exists():
                return ""
            
            # قراءة أول 1KB من الملف
            with open(file_path, 'rb') as f:
                content = f.read(1024)
                return hashlib.md5(content).hexdigest()
                
        except Exception as e:
            logger.error(f"❌ Error calculating content hash: {str(e)}")
            return ""
    
    # ============================================================
    # طرق التنظيف
    # ============================================================
    
    def cleanup_missing(self) -> List[str]:
        """
        تنظيف الملفات المفقودة
        
        Returns:
            قائمة المعرفات المحذوفة
        """
        missing = self.get_missing_files()
        removed = []
        
        for doc_id in missing:
            if self.remove_file(doc_id):
                removed.append(doc_id)
        
        if removed:
            self.save()
            logger.info(f"🗑️ Removed {len(removed)} missing files")
        
        return removed
    
    def sync_with_directory(
        self,
        directory_path: str,
        category: str,
        recursive: bool = True
    ) -> Dict[str, Any]:
        """
        مزامنة المجلد مع التعيينات
        
        Args:
            directory_path: مسار المجلد
            category: التصنيف
            recursive: بحث في المجلدات الفرعية
            
        Returns:
            نتائج المزامنة
        """
        path = Path(directory_path)
        
        if not path.exists():
            return {"error": "Directory not found"}
        
        # العثور على جميع الملفات
        pattern = "**/*" if recursive else "*"
        files = list(path.glob(pattern))
        files = [f for f in files if f.is_file()]
        
        results = {
            "added": [],
            "updated": [],
            "removed": [],
            "unchanged": [],
            "total": len(files)
        }
        
        # التحقق من كل ملف
        for file_path in files:
            file_str = str(file_path)
            
            if self.is_file_indexed(file_str):
                if self.has_file_changed(file_str):
                    # ملف متغير - تحديث
                    results["updated"].append(file_str)
                else:
                    results["unchanged"].append(file_str)
            else:
                # ملف جديد - إضافة
                results["added"].append(file_str)
        
        # حذف الملفات التي لم تعد موجودة
        for doc_id, info in self.mappings.items():
            if info.get("category") == category:
                file_path = Path(info.get("file_path", ""))
                if not file_path.exists():
                    results["removed"].append(doc_id)
        
        return results
