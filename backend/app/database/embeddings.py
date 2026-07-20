# backend/app/database/embeddings.py
"""
🧬 توليد المتجهات (Embeddings)

يقوم بتحويل النصوص إلى متجهات رقمية للبحث الدلالي
"""

import numpy as np
from typing import List, Union, Optional, Dict, Any
import asyncio
from concurrent.futures import ThreadPoolExecutor
import hashlib
import pickle
from pathlib import Path
import time

# محاولة استيراد Sentence Transformers
try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    print("⚠️ Sentence Transformers not available. Install with: pip install sentence-transformers")

from app.core.config import settings
from app.utils.logger import logger


class Embeddings:
    """
    توليد المتجهات للنصوص
    
    يدعم:
    - توليد متجهات لنص واحد
    - توليد متجهات لمجموعة نصوص
    - التخزين المؤقت للمتجهات
    - نماذج متعددة للاختيار
    """
    
    # قائمة النماذج المدعومة
    SUPPORTED_MODELS = {
        "all-MiniLM-L6-v2": {
            "dimension": 384,
            "description": "نموذج صغير وسريع (إنجليزي)",
            "language": "en"
        },
        "all-mpnet-base-v2": {
            "dimension": 768,
            "description": "نموذج متوسط الحجم (إنجليزي)",
            "language": "en"
        },
        "paraphrase-multilingual-MiniLM-L12-v2": {
            "dimension": 384,
            "description": "نموذج متعدد اللغات (يدعم العربية)",
            "language": "multi"
        },
        "distiluse-base-multilingual-cased-v2": {
            "dimension": 512,
            "description": "نموذج متعدد اللغات (يدعم العربية)",
            "language": "multi"
        }
    }
    
    def __init__(
        self,
        model_name: str = "paraphrase-multilingual-MiniLM-L12-v2",
        device: str = "cpu",
        cache_enabled: bool = True,
        cache_size: int = 10000
    ):
        """
        تهيئة أداة توليد المتجهات
        
        Args:
            model_name: اسم النموذج
            device: الجهاز (cpu أو cuda)
            cache_enabled: تفعيل التخزين المؤقت
            cache_size: حجم التخزين المؤقت
        """
        self.model_name = model_name
        self.device = device
        self.cache_enabled = cache_enabled
        self.cache_size = cache_size
        
        # التخزين المؤقت
        self.cache = {}
        self.cache_hits = 0
        self.cache_misses = 0
        
        # التحقق من النموذج
        if model_name not in self.SUPPORTED_MODELS:
            logger.warning(f"⚠️ Model {model_name} not in supported list. Using anyway.")
        
        # تحميل النموذج
        self.model = None
        self._load_model()
        
        # إحصائيات
        self.stats = {
            "total_embeddings": 0,
            "total_time": 0,
            "avg_time": 0,
            "batch_size": 0,
            "cache_hit_rate": 0
        }
        
        # تجمع الخيوط
        self.executor = ThreadPoolExecutor(max_workers=4)
        
        logger.info(f"🧬 Embeddings initialized with model: {model_name}")
    
    # ============================================================
    # الطريقة الرئيسية - توليد المتجهات
    # ============================================================
    
    async def encode(
        self,
        texts: Union[str, List[str]],
        normalize: bool = True,
        show_progress: bool = False,
        batch_size: int = 32
    ) -> np.ndarray:
        """
        توليد متجهات للنص أو النصوص
        
        Args:
            texts: النص أو قائمة النصوص
            normalize: تطبيع المتجهات
            show_progress: عرض تقدم المعالجة
            batch_size: حجم الدفعة
            
        Returns:
            مصفوفة المتجهات
        """
        start_time = time.time()
        
        # التحقق من النموذج
        if self.model is None:
            logger.error("❌ Model not loaded")
            return np.array([])
        
        # تحويل النص الواحد إلى قائمة
        if isinstance(texts, str):
            texts = [texts]
        
        # التحقق من التخزين المؤقت
        if self.cache_enabled:
            cached_embeddings, missing_indices = self._get_cached(texts)
        else:
            cached_embeddings = [None] * len(texts)
            missing_indices = list(range(len(texts)))
        
        # توليد المتجهات للنصوص غير المخزنة مؤقتاً
        if missing_indices:
            missing_texts = [texts[i] for i in missing_indices]
            
            # توليد المتجهات في الخلفية
            embeddings = await self._generate_embeddings(
                missing_texts,
                normalize=normalize,
                show_progress=show_progress,
                batch_size=batch_size
            )
            
            # تخزين في التخزين المؤقت
            if self.cache_enabled:
                for i, embedding in zip(missing_indices, embeddings):
                    self._add_to_cache(texts[i], embedding)
            
            # دمج النتائج
            result = []
            cache_idx = 0
            embed_idx = 0
            
            for i in range(len(texts)):
                if cached_embeddings[i] is not None:
                    result.append(cached_embeddings[i])
                else:
                    result.append(embeddings[embed_idx])
                    embed_idx += 1
            
            embeddings_array = np.array(result)
        else:
            embeddings_array = np.array(cached_embeddings)
        
        # تحديث الإحصائيات
        elapsed = time.time() - start_time
        self._update_stats(len(texts), elapsed)
        
        logger.debug(f"🧬 Generated {len(embeddings_array)} embeddings in {elapsed:.3f}s")
        
        return embeddings_array
    
    # ============================================================
    # طرق التوليد الداخلية
    # ============================================================
    
    async def _generate_embeddings(
        self,
        texts: List[str],
        normalize: bool = True,
        show_progress: bool = False,
        batch_size: int = 32
    ) -> List[np.ndarray]:
        """
        توليد المتجهات في الخلفية
        
        Args:
            texts: قائمة النصوص
            normalize: تطبيع المتجهات
            show_progress: عرض التقدم
            batch_size: حجم الدفعة
            
        Returns:
            قائمة المتجهات
        """
        # تشغيل في تجمع الخيوط
        loop = asyncio.get_event_loop()
        
        embeddings = await loop.run_in_executor(
            self.executor,
            self._encode_sync,
            texts,
            normalize,
            show_progress,
            batch_size
        )
        
        return embeddings
    
    def _encode_sync(
        self,
        texts: List[str],
        normalize: bool = True,
        show_progress: bool = False,
        batch_size: int = 32
    ) -> List[np.ndarray]:
        """
        توليد المتجهات بشكل متزامن
        
        Args:
            texts: قائمة النصوص
            normalize: تطبيع المتجهات
            show_progress: عرض التقدم
            batch_size: حجم الدفعة
            
        Returns:
            قائمة المتجهات
        """
        try:
            # توليد المتجهات باستخدام النموذج
            embeddings = self.model.encode(
                texts,
                normalize_embeddings=normalize,
                show_progress_bar=show_progress,
                batch_size=batch_size
            )
            
            # تحويل إلى قائمة
            if isinstance(embeddings, np.ndarray):
                return [emb for emb in embeddings]
            else:
                return list(embeddings)
                
        except Exception as e:
            logger.error(f"❌ Error generating embeddings: {str(e)}")
            return [np.array([]) for _ in texts]
    
    # ============================================================
    # طرق التخزين المؤقت (Cache)
    # ============================================================
    
    def _get_cache_key(self, text: str) -> str:
        """
        إنشاء مفتاح للتخزين المؤقت
        
        Args:
            text: النص
            
        Returns:
            مفتاح التخزين المؤقت
        """
        # استخدام النص نفسه كمفتاح (مع إزالة المسافات الزائدة)
        normalized = ' '.join(text.split())
        return hashlib.md5(normalized.encode()).hexdigest()
    
    def _get_cached(self, texts: List[str]) -> tuple:
        """
        الحصول على المتجهات من التخزين المؤقت
        
        Args:
            texts: قائمة النصوص
            
        Returns:
            (المتجهات المخزنة, مؤشرات النصوص غير المخزنة)
        """
        cached = []
        missing_indices = []
        
        for i, text in enumerate(texts):
            key = self._get_cache_key(text)
            if key in self.cache:
                cached.append(self.cache[key])
                self.cache_hits += 1
            else:
                cached.append(None)
                missing_indices.append(i)
                self.cache_misses += 1
        
        # تحديث نسبة النجاح
        total = self.cache_hits + self.cache_misses
        if total > 0:
            self.stats["cache_hit_rate"] = self.cache_hits / total
        
        return cached, missing_indices
    
    def _add_to_cache(self, text: str, embedding: np.ndarray) -> None:
        """
        إضافة متجه إلى التخزين المؤقت
        
        Args:
            text: النص
            embedding: المتجه
        """
        if not self.cache_enabled:
            return
        
        key = self._get_cache_key(text)
        
        # إذا كان التخزين المؤقت ممتلئاً
        if len(self.cache) >= self.cache_size:
            # حذف أول عنصر (FIFO)
            self.cache.pop(next(iter(self.cache)))
        
        self.cache[key] = embedding
    
    def clear_cache(self) -> None:
        """مسح التخزين المؤقت"""
        self.cache.clear()
        self.cache_hits = 0
        self.cache_misses = 0
        logger.info("🗑️ Embedding cache cleared")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """
        الحصول على إحصائيات التخزين المؤقت
        
        Returns:
            إحصائيات التخزين المؤقت
        """
        total = self.cache_hits + self.cache_misses
        return {
            "cache_size": len(self.cache),
            "cache_hits": self.cache_hits,
            "cache_misses": self.cache_misses,
            "hit_rate": self.cache_hits / total if total > 0 else 0,
            "max_cache_size": self.cache_size
        }
    
    # ============================================================
    # طرق إدارة النموذج
    # ============================================================
    
    def _load_model(self) -> None:
        """تحميل النموذج"""
        if not SENTENCE_TRANSFORMERS_AVAILABLE:
            logger.error("❌ Sentence Transformers not available")
            return
        
        try:
            self.model = SentenceTransformer(self.model_name, device=self.device)
            logger.info(f"✅ Model loaded: {self.model_name}")
            
            # تحديث أبعاد المتجهات
            if self.model_name in self.SUPPORTED_MODELS:
                self.dimension = self.SUPPORTED_MODELS[self.model_name]["dimension"]
            else:
                # اختبار النموذج لمعرفة الأبعاد
                test_embedding = self.model.encode(["test"])
                self.dimension = len(test_embedding[0])
                
        except Exception as e:
            logger.error(f"❌ Error loading model: {str(e)}")
            self.model = None
    
    def change_model(self, model_name: str) -> bool:
        """
        تغيير النموذج
        
        Args:
            model_name: اسم النموذج الجديد
            
        Returns:
            نجاح التغيير
        """
        if model_name == self.model_name:
            return True
        
        self.model_name = model_name
        self.clear_cache()
        self._load_model()
        
        return self.model is not None
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        الحصول على معلومات النموذج
        
        Returns:
            معلومات النموذج
        """
        info = {
            "model_name": self.model_name,
            "device": self.device,
            "is_loaded": self.model is not None,
            "dimension": self.dimension if hasattr(self, 'dimension') else None
        }
        
        if self.model_name in self.SUPPORTED_MODELS:
            info.update(self.SUPPORTED_MODELS[self.model_name])
        
        return info
    
    # ============================================================
    # طرق إضافية
    # ============================================================
    
    def _update_stats(self, count: int, elapsed: float) -> None:
        """
        تحديث الإحصائيات
        
        Args:
            count: عدد المتجهات
            elapsed: زمن المعالجة
        """
        self.stats["total_embeddings"] += count
        self.stats["total_time"] += elapsed
        
        # تحديث المتوسط
        total = self.stats["total_embeddings"]
        if total > 0:
            self.stats["avg_time"] = self.stats["total_time"] / total
    
    def get_stats(self) -> Dict[str, Any]:
        """
        الحصول على إحصائيات التوليد
        
        Returns:
            إحصائيات التوليد
        """
        return {
            **self.stats,
            "cache_stats": self.get_cache_stats(),
            "model_info": self.get_model_info()
        }
    
    def reset_stats(self) -> None:
        """إعادة تعيين الإحصائيات"""
        self.stats = {
            "total_embeddings": 0,
            "total_time": 0,
            "avg_time": 0,
            "batch_size": 0,
            "cache_hit_rate": 0
        }
        logger.info("🔄 Embedding stats reset")
    
    def get_dimension(self) -> int:
        """
        الحصول على أبعاد المتجهات
        
        Returns:
            أبعاد المتجهات
        """
        if hasattr(self, 'dimension'):
            return self.dimension
        
        # اختبار النموذج
        if self.model:
            test_embedding = self.model.encode(["test"])
            self.dimension = len(test_embedding[0])
            return self.dimension
        
        return 0
    
    def save_embeddings(self, embeddings: np.ndarray, file_path: str) -> bool:
        """
        حفظ المتجهات إلى ملف
        
        Args:
            embeddings: مصفوفة المتجهات
            file_path: مسار الملف
            
        Returns:
            نجاح الحفظ
        """
        try:
            with open(file_path, 'wb') as f:
                pickle.dump(embeddings, f)
            logger.info(f"✅ Embeddings saved to {file_path}")
            return True
        except Exception as e:
            logger.error(f"❌ Error saving embeddings: {str(e)}")
            return False
    
    def load_embeddings(self, file_path: str) -> Optional[np.ndarray]:
        """
        تحميل المتجهات من ملف
        
        Args:
            file_path: مسار الملف
            
        Returns:
            مصفوفة المتجهات
        """
        try:
            with open(file_path, 'rb') as f:
                embeddings = pickle.load(f)
            logger.info(f"✅ Embeddings loaded from {file_path}")
            return embeddings
        except Exception as e:
            logger.error(f"❌ Error loading embeddings: {str(e)}")
            return None
    
    def similarity(self, embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        """
        حساب التشابه بين متجهين
        
        Args:
            embedding1: المتجه الأول
            embedding2: المتجه الثاني
            
        Returns:
            درجة التشابه (0-1)
        """
        if len(embedding1) != len(embedding2):
            return 0.0
        
        # تطبيع المتجهات
        norm1 = np.linalg.norm(embedding1)
        norm2 = np.linalg.norm(embedding2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        # حساب التشابه (جيب التمام)
        similarity = np.dot(embedding1, embedding2) / (norm1 * norm2)
        
        # تطبيع إلى (0-1)
        return (similarity + 1) / 2
