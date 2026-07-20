# backend/app/rag/semantic_search.py
"""
🔍 البحث الدلالي (Semantic Search)

يقوم بالبحث الدلالي باستخدام المتجهات (Embeddings) للعثور على النصوص الأكثر تشابهاً
"""

from typing import List, Dict, Any, Optional, Tuple
import numpy as np
import faiss
import pickle
import json
from pathlib import Path
import hashlib
from datetime import datetime
import asyncio
from concurrent.futures import ThreadPoolExecutor

from app.core.config import settings
from app.database.embeddings import Embeddings
from app.database.faiss_loader import FAISSLoader
from app.utils.logger import logger


class SemanticSearch:
    """
    البحث الدلالي باستخدام المتجهات
    
    يدعم:
    - البحث الدلالي الأساسي
    - البحث مع إعادة الترتيب
    - البحث عن النصوص المتشابهة
    - تجميع النتائج حسب الموضوع
    - البحث عبر أقسام مختلفة
    """
    
    def __init__(
        self,
        embeddings: Optional[Embeddings] = None,
        faiss_loader: Optional[FAISSLoader] = None,
        top_k: int = 10,
        min_score: float = 0.3
    ):
        """
        تهيئة أداة البحث الدلالي
        
        Args:
            embeddings: أداة توليد المتجهات
            faiss_loader: محمل فهرس FAISS
            top_k: عدد النتائج الافتراضي
            min_score: الحد الأدنى لدرجة المطابقة
        """
        self.embeddings = embeddings or Embeddings()
        self.faiss_loader = faiss_loader or FAISSLoader()
        self.top_k = top_k
        self.min_score = min_score
        
        # إحصائيات
        self.stats = {
            "total_searches": 0,
            "avg_search_time": 0,
            "total_results": 0,
            "last_search_time": 0
        }
        
        # تجمع الخيوط للعمليات المتوازية
        self.executor = ThreadPoolExecutor(max_workers=4)
        
        logger.info("🔍 Semantic Search initialized")
    
    # ============================================================
    # البحث الأساسي
    # ============================================================
    
    async def search(
        self,
        query: str,
        top_k: Optional[int] = None,
        min_score: Optional[float] = None,
        filter_category: Optional[str] = None,
        filter_supplier: Optional[str] = None,
        return_scores: bool = True
    ) -> List[Dict[str, Any]]:
        """
        البحث الدلالي الأساسي
        
        Args:
            query: نص البحث
            top_k: عدد النتائج المطلوبة
            min_score: الحد الأدنى للدرجة
            filter_category: تصفية حسب التصنيف
            filter_supplier: تصفية حسب المورد
            return_scores: إرجاع الدرجات مع النتائج
            
        Returns:
            قائمة النتائج
        """
        import time
        start_time = time.time()
        
        logger.info(f"🔍 Semantic search: '{query[:50]}...'")
        
        # 1. توليد متجه للاستعلام
        query_vector = await self.embeddings.encode(query)
        
        # 2. البحث في FAISS
        results = await self.faiss_loader.search(
            query_vector=query_vector,
            top_k=top_k or self.top_k
        )
        
        # 3. تصفية النتائج
        filtered_results = self._filter_results(
            results,
            min_score=min_score or self.min_score,
            filter_category=filter_category,
            filter_supplier=filter_supplier
        )
        
        # 4. تنسيق النتائج
        formatted_results = self._format_results(
            filtered_results,
            return_scores=return_scores
        )
        
        # 5. تحديث الإحصائيات
        elapsed = time.time() - start_time
        self._update_stats(len(formatted_results), elapsed)
        
        logger.info(f"✅ Found {len(formatted_results)} results in {elapsed:.3f}s")
        
        return formatted_results
    
    # ============================================================
    # البحث المتقدم
    # ============================================================
    
    async def search_batch(
        self,
        queries: List[str],
        top_k: Optional[int] = None,
        min_score: Optional[float] = None,
        **kwargs
    ) -> List[List[Dict[str, Any]]]:
        """
        البحث عن مجموعة من الاستعلامات (متوازي)
        
        Args:
            queries: قائمة نصوص البحث
            top_k: عدد النتائج لكل بحث
            min_score: الحد الأدنى للدرجة
            
        Returns:
            قائمة بنتائج كل بحث
        """
        logger.info(f"🔍 Batch search: {len(queries)} queries")
        
        # إنشاء المهام المتوازية
        tasks = [
            self.search(query, top_k=top_k, min_score=min_score, **kwargs)
            for query in queries
        ]
        
        # تنفيذ المهام بشكل متوازي
        results = await asyncio.gather(*tasks)
        
        logger.info(f"✅ Batch search completed: {len(results)} queries")
        
        return results
    
    async def search_similar(
        self,
        text: str,
        top_k: Optional[int] = None,
        threshold: float = 0.5
    ) -> List[Dict[str, Any]]:
        """
        البحث عن نصوص مشابهة لنص معين
        
        Args:
            text: النص المرجعي
            top_k: عدد النتائج المطلوبة
            threshold: حد التشابه المطلوب
            
        Returns:
            قائمة النصوص المشابهة
        """
        # توليد متجه للنص المرجعي
        text_vector = await self.embeddings.encode(text)
        
        # البحث في FAISS
        results = await self.faiss_loader.search(
            query_vector=text_vector,
            top_k=top_k or self.top_k * 2
        )
        
        # تصفية حسب حد التشابه
        filtered = [
            result for result in results
            if result.get("relevance_score", 0) >= threshold
        ]
        
        # تنسيق النتائج
        formatted = self._format_results(filtered, return_scores=True)
        
        return formatted
    
    async def search_by_category(
        self,
        query: str,
        category: str,
        top_k: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        البحث داخل تصنيف معين فقط
        
        Args:
            query: نص البحث
            category: التصنيف المطلوب
            top_k: عدد النتائج
            
        Returns:
            قائمة النتائج من التصنيف المطلوب
        """
        return await self.search(
            query=query,
            top_k=top_k,
            filter_category=category
        )
    
    async def search_by_supplier(
        self,
        query: str,
        supplier: str,
        top_k: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        البحث داخل مورد معين فقط
        
        Args:
            query: نص البحث
            supplier: اسم المورد
            top_k: عدد النتائج
            
        Returns:
            قائمة النتائج من المورد المطلوب
        """
        return await self.search(
            query=query,
            top_k=top_k,
            filter_supplier=supplier
        )
    
    # ============================================================
    # طرق البحث المتخصصة
    # ============================================================
    
    async def search_contracts(self, query: str, top_k: Optional[int] = None) -> List[Dict[str, Any]]:
        """البحث في العقود فقط"""
        return await self.search_by_category(query, "contracts", top_k)
    
    async def search_policies(self, query: str, top_k: Optional[int] = None) -> List[Dict[str, Any]]:
        """البحث في السياسات فقط"""
        return await self.search_by_category(query, "policies", top_k)
    
    async def search_quotations(self, query: str, top_k: Optional[int] = None) -> List[Dict[str, Any]]:
        """البحث في عروض الأسعار فقط"""
        return await self.search_by_category(query, "quotations", top_k)
    
    async def search_quality_reports(self, query: str, top_k: Optional[int] = None) -> List[Dict[str, Any]]:
        """البحث في تقارير الجودة فقط"""
        return await self.search_by_category(query, "quality_reports", top_k)
    
    # ============================================================
    # طرق التحليل والتجميع
    # ============================================================
    
    async def cluster_results(
        self,
        query: str,
        top_k: Optional[int] = None,
        num_clusters: int = 3
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        تجميع النتائج حسب الموضوع
        
        Args:
            query: نص البحث
            top_k: عدد النتائج
            num_clusters: عدد المجموعات
            
        Returns:
            النتائج مجمعة حسب الموضوع
        """
        # الحصول على النتائج
        results = await self.search(query, top_k=top_k or self.top_k * 2)
        
        if len(results) < num_clusters:
            return {"all": results}
        
        try:
            # استخراج المتجهات للنتائج
            vectors = []
            for result in results:
                text = result.get("text", "")
                if text:
                    vector = await self.embeddings.encode(text)
                    vectors.append(vector)
            
            if not vectors:
                return {"all": results}
            
            # تحويل إلى مصفوفة
            vectors = np.array(vectors)
            
            # تطبيق K-Means للتجميع
            from sklearn.cluster import KMeans
            kmeans = KMeans(n_clusters=min(num_clusters, len(vectors)), random_state=42)
            labels = kmeans.fit_predict(vectors)
            
            # تجميع النتائج حسب التصنيف
            clustered = {}
            for i, label in enumerate(labels):
                label_str = f"cluster_{label}"
                if label_str not in clustered:
                    clustered[label_str] = []
                clustered[label_str].append(results[i])
            
            return clustered
            
        except Exception as e:
            logger.warning(f"⚠️ Clustering failed: {e}")
            return {"all": results}
    
    async def get_related_questions(
        self,
        query: str,
        top_k: int = 5
    ) -> List[str]:
        """
        الحصول على أسئلة مرتبطة بالسؤال
        
        Args:
            query: السؤال الأصلي
            top_k: عدد الأسئلة المرتبطة
            
        Returns:
            قائمة الأسئلة المرتبطة
        """
        # البحث عن نصوص مشابهة
        results = await self.search_similar(query, top_k=top_k * 2, threshold=0.3)
        
        # استخراج الأسئلة من النتائج
        questions = []
        for result in results:
            text = result.get("text", "")
            # محاولة استخراج أسئلة من النص
            extracted = self._extract_questions(text)
            questions.extend(extracted)
        
        # إزالة التكرار واختيار الأفضل
        unique_questions = list(dict.fromkeys(questions))[:top_k]
        
        return unique_questions
    
    # ============================================================
    # طرق مساعدة
    # ============================================================
    
    def _filter_results(
        self,
        results: List[Dict[str, Any]],
        min_score: float,
        filter_category: Optional[str] = None,
        filter_supplier: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        تصفية النتائج
        
        Args:
            results: قائمة النتائج
            min_score: الحد الأدنى للدرجة
            filter_category: تصفية حسب التصنيف
            filter_supplier: تصفية حسب المورد
            
        Returns:
            قائمة النتائج المصفاة
        """
        filtered = []
        
        for result in results:
            # تصفية حسب الدرجة
            score = result.get("relevance_score", 0)
            if score < min_score:
                continue
            
            metadata = result.get("metadata", {})
            
            # تصفية حسب التصنيف
            if filter_category:
                if metadata.get("category") != filter_category:
                    continue
            
            # تصفية حسب المورد
            if filter_supplier:
                if metadata.get("supplier") != filter_supplier:
                    continue
            
            filtered.append(result)
        
        return filtered
    
    def _format_results(
        self,
        results: List[Dict[str, Any]],
        return_scores: bool = True
    ) -> List[Dict[str, Any]]:
        """
        تنسيق النتائج للعرض
        
        Args:
            results: قائمة النتائج
            return_scores: إرجاع الدرجات
            
        Returns:
            قائمة النتائج المنسقة
        """
        formatted = []
        
        for i, result in enumerate(results, 1):
            formatted_result = {
                "id": result.get("id", f"result_{i}"),
                "text": result.get("text", ""),
                "metadata": result.get("metadata", {}),
                "rank": i
            }
            
            if return_scores:
                formatted_result["relevance_score"] = result.get("relevance_score", 0)
            
            formatted.append(formatted_result)
        
        return formatted
    
    def _extract_questions(self, text: str) -> List[str]:
        """
        استخراج الأسئلة من النص
        
        Args:
            text: النص
            
        Returns:
            قائمة الأسئلة
        """
        import re
        
        # كلمات استفهام في العربية والإنجليزية
        question_words = ["ما", "ماذا", "كيف", "لماذا", "متى", "أين", "هل", "من",
                         "ما هي", "ما هو", "كيفية", "إيه", "ليش",
                         "what", "how", "why", "when", "where", "who", "which"]
        
        questions = []
        
        # تقسيم النص إلى جمل
        sentences = re.split(r'[.!?،؛؟\n]', text)
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
            
            # التحقق من وجود كلمة استفهام
            for word in question_words:
                if word in sentence.lower():
                    # تنظيف الجملة
                    clean = sentence.strip(".,،;؟! ")
                    if len(clean) > 10:  # تجاهل الجمل القصيرة جداً
                        questions.append(clean)
                    break
        
        return questions[:5]  # حد أقصى 5 أسئلة
    
    def _update_stats(self, count: int, elapsed: float) -> None:
        """
        تحديث الإحصائيات
        
        Args:
            count: عدد النتائج
            elapsed: زمن المعالجة
        """
        self.stats["total_searches"] += 1
        self.stats["total_results"] += count
        self.stats["last_search_time"] = elapsed
        
        # تحديث المتوسط
        total = self.stats["total_searches"]
        if total > 0:
            self.stats["avg_search_time"] = (
                (self.stats["avg_search_time"] * (total - 1) + elapsed) / total
            )
    
    # ============================================================
    # طرق إحصائيات وإدارة
    # ============================================================
    
    def get_stats(self) -> Dict[str, Any]:
        """
        الحصول على إحصائيات البحث
        
        Returns:
            إحصائيات البحث
        """
        return {
            **self.stats,
            "top_k": self.top_k,
            "min_score": self.min_score,
            "index_size": self.faiss_loader.get_index_size(),
            "model_name": self.embeddings.model_name
        }
    
    def reset(self) -> None:
        """إعادة تعيين الإحصائيات"""
        self.stats = {
            "total_searches": 0,
            "avg_search_time": 0,
            "total_results": 0,
            "last_search_time": 0
        }
        logger.info("🔄 Semantic Search stats reset")
    
    def get_index_info(self) -> Dict[str, Any]:
        """
        الحصول على معلومات الفهرس
        
        Returns:
            معلومات الفهرس
        """
        return self.faiss_loader.get_index_info()
