# backend/app/database/faiss_loader.py
"""
🗄️ تحميل وإدارة فهرس FAISS

يقوم بتحميل فهرس FAISS والبحث فيه واسترجاع المستندات
"""

import os
import pickle
import json
import numpy as np
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import hashlib
from datetime import datetime

# محاولة استيراد FAISS
try:
    import faiss
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False
    print("⚠️ FAISS not available. Install with: pip install faiss-cpu")

from app.core.config import settings
from app.utils.logger import logger


class FAISSLoader:
    """
    تحميل وإدارة فهرس FAISS
    
    يدعم:
    - تحميل فهرس FAISS من القرص
    - البحث في الفهرس
    - إضافة مستندات جديدة
    - حذف مستندات
    - إعادة بناء الفهرس
    """
    
    def __init__(
        self,
        index_path: Optional[str] = None,
        metadata_path: Optional[str] = None,
        dimension: int = 384
    ):
        """
        تهيئة أداة تحميل FAISS
        
        Args:
            index_path: مسار ملف الفهرس
            metadata_path: مسار ملف البيانات الوصفية
            dimension: أبعاد المتجهات
        """
        self.index_path = Path(index_path or settings.FAISS_INDEX_PATH / "index.faiss")
        self.metadata_path = Path(metadata_path or settings.FAISS_INDEX_PATH / "metadata.pkl")
        self.dimension = dimension
        
        # تحميل الفهرس والبيانات الوصفية
        self.index = None
        self.metadata = []
        self.is_loaded = False
        
        # إحصائيات
        self.stats = {
            "total_documents": 0,
            "total_searches": 0,
            "avg_search_time": 0,
            "last_search_time": 0
        }
        
        # تحميل الفهرس
        self.load()
        
        logger.info("🗄️ FAISSLoader initialized")
    
    # ============================================================
    # طرق التحميل والحفظ
    # ============================================================
    
    def load(self) -> bool:
        """
        تحميل الفهرس والبيانات الوصفية من القرص
        
        Returns:
            نجاح التحميل
        """
        try:
            # تحميل الفهرس
            if self.index_path.exists():
                self.index = faiss.read_index(str(self.index_path))
                logger.info(f"✅ FAISS index loaded: {self.index_path}")
            else:
                logger.warning(f"⚠️ FAISS index not found: {self.index_path}")
                self._create_empty_index()
            
            # تحميل البيانات الوصفية
            if self.metadata_path.exists():
                with open(self.metadata_path, 'rb') as f:
                    self.metadata = pickle.load(f)
                logger.info(f"✅ Metadata loaded: {len(self.metadata)} documents")
            else:
                logger.warning(f"⚠️ Metadata not found: {self.metadata_path}")
                self.metadata = []
            
            self.is_loaded = True
            self.stats["total_documents"] = len(self.metadata)
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error loading FAISS: {str(e)}")
            self.is_loaded = False
            return False
    
    def save(self) -> bool:
        """
        حفظ الفهرس والبيانات الوصفية إلى القرص
        
        Returns:
            نجاح الحفظ
        """
        try:
            if self.index is None:
                logger.warning("⚠️ No index to save")
                return False
            
            # إنشاء المجلد إذا لم يكن موجوداً
            self.index_path.parent.mkdir(parents=True, exist_ok=True)
            
            # حفظ الفهرس
            faiss.write_index(self.index, str(self.index_path))
            
            # حفظ البيانات الوصفية
            with open(self.metadata_path, 'wb') as f:
                pickle.dump(self.metadata, f)
            
            logger.info(f"✅ FAISS index saved: {self.index_path}")
            logger.info(f"✅ Metadata saved: {len(self.metadata)} documents")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error saving FAISS: {str(e)}")
            return False
    
    def _create_empty_index(self) -> None:
        """إنشاء فهرس فارغ"""
        self.index = faiss.IndexFlatL2(self.dimension)
        logger.info("📁 Created empty FAISS index")
    
    # ============================================================
    # طرق البحث
    # ============================================================
    
    async def search(
        self,
        query_vector: np.ndarray,
        top_k: int = 10,
        include_metadata: bool = True
    ) -> List[Dict[str, Any]]:
        """
        البحث في الفهرس
        
        Args:
            query_vector: متجه الاستعلام
            top_k: عدد النتائج
            include_metadata: تضمين البيانات الوصفية
            
        Returns:
            قائمة النتائج
        """
        import time
        start_time = time.time()
        
        if not self.is_loaded or self.index is None:
            logger.error("❌ FAISS not loaded")
            return []
        
        if len(self.metadata) == 0:
            logger.warning("⚠️ No documents in index")
            return []
        
        try:
            # تحويل المتجه إلى الشكل المناسب
            if len(query_vector.shape) == 1:
                query_vector = query_vector.reshape(1, -1)
            
            # البحث في الفهرس
            distances, indices = self.index.search(query_vector.astype('float32'), top_k)
            
            # تجهيز النتائج
            results = []
            for i, (dist, idx) in enumerate(zip(distances[0], indices[0])):
                if idx == -1 or idx >= len(self.metadata):
                    continue
                
                # حساب درجة المطابقة (تحويل المسافة إلى درجة)
                similarity = self._distance_to_similarity(dist)
                
                result = {
                    "id": self.metadata[idx].get("id", f"doc_{idx}"),
                    "text": self.metadata[idx].get("text", ""),
                    "metadata": self.metadata[idx].get("metadata", {}),
                    "relevance_score": similarity,
                    "distance": float(dist),
                    "index": int(idx)
                }
                
                results.append(result)
            
            # تحديث الإحصائيات
            elapsed = time.time() - start_time
            self._update_stats(len(results), elapsed)
            
            logger.debug(f"🔍 Found {len(results)} results in {elapsed:.3f}s")
            
            return results
            
        except Exception as e:
            logger.error(f"❌ Error searching FAISS: {str(e)}")
            return []
    
    def search_sync(
        self,
        query_vector: np.ndarray,
        top_k: int = 10
    ) -> Tuple[List[int], List[float]]:
        """
        بحث متزامن (للاستخدام الداخلي)
        
        Args:
            query_vector: متجه الاستعلام
            top_k: عدد النتائج
            
        Returns:
            (المؤشرات, المسافات)
        """
        if not self.is_loaded or self.index is None:
            return [], []
        
        if len(self.metadata) == 0:
            return [], []
        
        try:
            if len(query_vector.shape) == 1:
                query_vector = query_vector.reshape(1, -1)
            
            distances, indices = self.index.search(
                query_vector.astype('float32'),
                min(top_k, len(self.metadata))
            )
            
            return indices[0].tolist(), distances[0].tolist()
            
        except Exception as e:
            logger.error(f"❌ Error in sync search: {str(e)}")
            return [], []
    
    # ============================================================
    # طرق إدارة المستندات
    # ============================================================
    
    def add_document(
        self,
        doc_id: str,
        text: str,
        embedding: np.ndarray,
        metadata: Dict[str, Any]
    ) -> bool:
        """
        إضافة مستند جديد إلى الفهرس
        
        Args:
            doc_id: معرف المستند
            text: نص المستند
            embedding: متجه المستند
            metadata: البيانات الوصفية
            
        Returns:
            نجاح الإضافة
        """
        try:
            if self.index is None:
                self._create_empty_index()
            
            # تحويل المتجه إلى الشكل المناسب
            if len(embedding.shape) == 1:
                embedding = embedding.reshape(1, -1)
            
            # إضافة إلى الفهرس
            self.index.add(embedding.astype('float32'))
            
            # إضافة البيانات الوصفية
            doc_data = {
                "id": doc_id,
                "text": text,
                "metadata": metadata,
                "added_at": datetime.now().isoformat()
            }
            self.metadata.append(doc_data)
            
            self.stats["total_documents"] = len(self.metadata)
            
            logger.info(f"✅ Document added: {doc_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error adding document: {str(e)}")
            return False
    
    def delete_document(self, doc_id: str) -> bool:
        """
        حذف مستند من الفهرس
        
        ملاحظة: FAISS لا يدعم الحذف المباشر، نعيد بناء الفهرس
        
        Args:
            doc_id: معرف المستند
            
        Returns:
            نجاح الحذف
        """
        try:
            # العثور على المؤشر
            idx = None
            for i, doc in enumerate(self.metadata):
                if doc.get("id") == doc_id:
                    idx = i
                    break
            
            if idx is None:
                logger.warning(f"⚠️ Document not found: {doc_id}")
                return False
            
            # حذف من البيانات الوصفية
            self.metadata.pop(idx)
            
            # إعادة بناء الفهرس (لأن FAISS لا يدعم الحذف)
            self._rebuild_index()
            
            self.stats["total_documents"] = len(self.metadata)
            
            logger.info(f"✅ Document deleted: {doc_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error deleting document: {str(e)}")
            return False
    
    def update_document(
        self,
        doc_id: str,
        text: str,
        embedding: np.ndarray,
        metadata: Dict[str, Any]
    ) -> bool:
        """
        تحديث مستند في الفهرس
        
        Args:
            doc_id: معرف المستند
            text: النص الجديد
            embedding: المتجه الجديد
            metadata: البيانات الوصفية الجديدة
            
        Returns:
            نجاح التحديث
        """
        try:
            # حذف المستند القديم
            self.delete_document(doc_id)
            
            # إضافة المستند الجديد
            return self.add_document(doc_id, text, embedding, metadata)
            
        except Exception as e:
            logger.error(f"❌ Error updating document: {str(e)}")
            return False
    
    def _rebuild_index(self) -> None:
        """إعادة بناء الفهرس من البيانات الوصفية"""
        # إنشاء فهرس جديد
        self._create_empty_index()
        
        # لا يمكن إعادة بناء المتجهات من البيانات الوصفية
        # نحتاج إلى حفظ المتجهات بشكل منفصل
        logger.warning("⚠️ Rebuilding index requires embeddings. Use rebuild_from_embeddings()")
    
    def rebuild_from_embeddings(self, embeddings: List[np.ndarray]) -> bool:
        """
        إعادة بناء الفهرس من المتجهات
        
        Args:
            embeddings: قائمة المتجهات
            
        Returns:
            نجاح إعادة البناء
        """
        try:
            if len(embeddings) != len(self.metadata):
                logger.error("❌ Embeddings count doesn't match metadata")
                return False
            
            # إنشاء فهرس جديد
            self._create_empty_index()
            
            # إضافة جميع المتجهات
            for embedding in embeddings:
                if len(embedding.shape) == 1:
                    embedding = embedding.reshape(1, -1)
                self.index.add(embedding.astype('float32'))
            
            self.stats["total_documents"] = len(self.metadata)
            
            logger.info(f"✅ Index rebuilt with {len(embeddings)} documents")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error rebuilding index: {str(e)}")
            return False
    
    # ============================================================
    # طرق مساعدة
    # ============================================================
    
    def _distance_to_similarity(self, distance: float) -> float:
        """
        تحويل المسافة إلى درجة مطابقة (0-1)
        
        Args:
            distance: المسافة (L2)
            
        Returns:
            درجة المطابقة
        """
        # تحويل المسافة L2 إلى تشابه (كلما كانت المسافة أصغر، التشابه أكبر)
        # نطاق المسافات عادة بين 0 و 2
        similarity = 1 / (1 + distance)
        
        # تطبيع إلى (0-1)
        return min(max(similarity, 0.0), 1.0)
    
    def _update_stats(self, count: int, elapsed: float) -> None:
        """
        تحديث الإحصائيات
        
        Args:
            count: عدد النتائج
            elapsed: زمن المعالجة
        """
        self.stats["total_searches"] += 1
        self.stats["last_search_time"] = elapsed
        
        total = self.stats["total_searches"]
        if total > 0:
            self.stats["avg_search_time"] = (
                (self.stats["avg_search_time"] * (total - 1) + elapsed) / total
            )
    
    # ============================================================
    # طرق الإحصائيات والمعلومات
    # ============================================================
    
    def get_stats(self) -> Dict[str, Any]:
        """
        الحصول على إحصائيات الفهرس
        
        Returns:
            إحصائيات الفهرس
        """
        return {
            **self.stats,
            "is_loaded": self.is_loaded,
            "dimension": self.dimension,
            "index_path": str(self.index_path),
            "metadata_path": str(self.metadata_path)
        }
    
    def get_index_info(self) -> Dict[str, Any]:
        """
        الحصول على معلومات الفهرس
        
        Returns:
            معلومات الفهرس
        """
        if self.index is None:
            return {"status": "not_loaded"}
        
        return {
            "status": "loaded",
            "total_vectors": self.index.ntotal,
            "dimension": self.index.d,
            "index_type": type(self.index).__name__,
            "is_trained": self.index.is_trained,
            "metadata_count": len(self.metadata)
        }
    
    def get_document(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """
        الحصول على مستند بواسطة معرفه
        
        Args:
            doc_id: معرف المستند
            
        Returns:
            المستند أو None
        """
        for doc in self.metadata:
            if doc.get("id") == doc_id:
                return doc
        return None
    
    def get_all_documents(self) -> List[Dict[str, Any]]:
        """
        الحصول على جميع المستندات
        
        Returns:
            قائمة جميع المستندات
        """
        return self.metadata.copy()
    
    def get_index_size(self) -> int:
        """
        الحصول على حجم الفهرس
        
        Returns:
            عدد المستندات في الفهرس
        """
        return len(self.metadata)
    
    def clear(self) -> None:
        """مسح الفهرس بالكامل"""
        self._create_empty_index()
        self.metadata = []
        self.stats["total_documents"] = 0
        self.is_loaded = True
        logger.info("🗑️ FAISS index cleared")
    
    # ============================================================
    # طرق التحقق من الصحة
    # ============================================================
    
    async def check_health(self) -> bool:
        """
        التحقق من صحة الفهرس
        
        Returns:
            صحة الفهرس
        """
        try:
            if not self.is_loaded:
                return False
            
            if self.index is None:
                return False
            
            # اختبار البحث
            test_vector = np.random.randn(1, self.dimension).astype('float32')
            self.index.search(test_vector, 1)
            
            return True
            
        except Exception as e:
            logger.error(f"❌ FAISS health check failed: {str(e)}")
            return False
