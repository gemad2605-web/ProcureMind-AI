# backend/app/rag/qa_engine.py
"""
🧠 محرك الأسئلة والأجوبة (QA Engine)

يدير تدفق RAG بالكامل:
1. استرجاع المستندات
2. إعادة ترتيب النتائج
3. بناء السياق
4. توليد الإجابة
"""

from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
import time
import hashlib
from datetime import datetime

from app.rag.retriever import Retriever
from app.rag.reranker import Reranker
from app.rag.chunking import Chunking, Chunk
from app.llm.grok_client import GrokClient
from app.core.config import settings
from app.core.prompts import RAG_PROMPTS
from app.utils.logger import logger


@dataclass
class QAResult:
    """
    نتيجة محرك الأسئلة والأجوبة
    """
    question: str
    answer: str
    sources: List[Dict[str, Any]]
    confidence_score: float
    processing_time: float
    retrieved_count: int
    reranked_count: int
    chunks_used: int
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    metadata: Dict[str, Any] = field(default_factory=dict)


class QAEngine:
    """
    محرك الأسئلة والأجوبة (RAG Pipeline)
    
    يقوم بتنفيذ تدفق RAG بالكامل:
    1. استرجاع المستندات من FAISS
    2. إعادة ترتيب النتائج
    3. بناء السياق
    4. توليد الإجابة باستخدام LLM
    """
    
    def __init__(
        self,
        retriever: Optional[Retriever] = None,
        reranker: Optional[Reranker] = None,
        chunking: Optional[Chunking] = None,
        llm: Optional[GrokClient] = None
    ):
        """
        تهيئة محرك الأسئلة والأجوبة
        
        Args:
            retriever: أداة الاسترجاع
            reranker: أداة إعادة الترتيب
            chunking: أداة التقسيم
            llm: عميل النموذج اللغوي
        """
        self.retriever = retriever or Retriever()
        self.reranker = reranker or Reranker()
        self.chunking = chunking or Chunking()
        self.llm = llm or GrokClient()
        
        self.default_top_k = settings.DEFAULT_TOP_K
        self.default_max_sources = settings.DEFAULT_MAX_SOURCES
        self.min_confidence = settings.MIN_CONFIDENCE_SCORE
        
        logger.info("🧠 QA Engine initialized successfully")
    
    # ============================================================
    # الطريقة الرئيسية
    # ============================================================
    
    async def answer(
        self,
        question: str,
        top_k: int = None,
        max_sources: int = None,
        temperature: float = None,
        include_sources: bool = True,
        filter_category: Optional[str] = None,
        filter_supplier: Optional[str] = None,
        **kwargs
    ) -> QAResult:
        """
        الإجابة على سؤال باستخدام RAG
        
        Args:
            question: سؤال المستخدم
            top_k: عدد المستندات المسترجعة
            max_sources: الحد الأقصى للمصادر
            temperature: درجة الإبداع
            include_sources: عرض المصادر
            filter_category: تصفية حسب التصنيف
            filter_supplier: تصفية حسب المورد
            
        Returns:
            QAResult: نتيجة السؤال
        """
        start_time = time.time()
        
        logger.info(f"🧠 Processing question: {question[:50]}...")
        
        # 1. إعداد المعلمات
        top_k = top_k or self.default_top_k
        max_sources = max_sources or self.default_max_sources
        temperature = temperature or settings.DEFAULT_TEMPERATURE
        
        # 2. تحسين السؤال
        enhanced_question = self._enhance_question(question)
        
        # 3. استرجاع المستندات
        retrieved_docs = await self.retriever.retrieve(
            query=enhanced_question,
            top_k=top_k,
            filter_category=filter_category,
            filter_supplier=filter_supplier
        )
        
        retrieved_count = len(retrieved_docs)
        logger.info(f"📚 Retrieved {retrieved_count} documents")
        
        # 4. إعادة ترتيب النتائج
        reranked_docs = await self.reranker.rerank(
            query=question,
            documents=retrieved_docs,
            top_k=max_sources
        )
        
        reranked_count = len(reranked_docs)
        logger.info(f"📊 Reranked to {reranked_count} documents")
        
        # 5. بناء السياق
        context = self._build_context(reranked_docs)
        chunks_used = len(reranked_docs)
        
        # 6. توليد الإجابة
        answer = await self.llm.generate(
            question=question,
            context=context,
            temperature=temperature,
            system_prompt=kwargs.get("system_prompt")
        )
        
        # 7. حساب درجة الثقة
        confidence_score = self._calculate_confidence(
            reranked_docs,
            len(answer),
            chunks_used
        )
        
        # 8. تجهيز المصادر
        sources = []
        if include_sources:
            sources = self._format_sources(reranked_docs)
        
        # 9. حساب زمن المعالجة
        processing_time = time.time() - start_time
        
        # 10. بناء النتيجة
        result = QAResult(
            question=question,
            answer=answer,
            sources=sources,
            confidence_score=confidence_score,
            processing_time=processing_time,
            retrieved_count=retrieved_count,
            reranked_count=reranked_count,
            chunks_used=chunks_used,
            metadata={
                "temperature": temperature,
                "top_k": top_k,
                "max_sources": max_sources,
                "filter_category": filter_category,
                "filter_supplier": filter_supplier,
                "enhanced_question": enhanced_question if enhanced_question != question else None
            }
        )
        
        logger.info(f"✅ Answer generated in {processing_time:.2f}s")
        
        return result
    
    # ============================================================
    # طرق بناء السياق
    # ============================================================
    
    def _build_context(self, documents: List[Dict[str, Any]]) -> str:
        """
        بناء السياق من المستندات المسترجعة
        
        Args:
            documents: قائمة المستندات
            
        Returns:
            النص السياقي
        """
        if not documents:
            return "لا توجد معلومات كافية للإجابة على هذا السؤال."
        
        context_parts = []
        
        for i, doc in enumerate(documents, 1):
            # إضافة رقم المستند ومصدره
            source = doc.get("metadata", {}).get("filename", f"مصدر {i}")
            category = doc.get("metadata", {}).get("category", "غير مصنف")
            relevance = doc.get("relevance_score", 0.0)
            
            context_parts.append(f"[{i}] المصدر: {source}")
            context_parts.append(f"    التصنيف: {category}")
            context_parts.append(f"    درجة المطابقة: {relevance:.2%}")
            context_parts.append(f"    المحتوى:\n    {doc.get('text', '')}")
            context_parts.append("")
        
        return "\n".join(context_parts)
    
    def _build_context_chunks(self, chunks: List[Chunk]) -> str:
        """
        بناء السياق من قطع النصوص
        
        Args:
            chunks: قائمة القطع النصية
            
        Returns:
            النص السياقي
        """
        if not chunks:
            return "لا توجد معلومات كافية."
        
        context_parts = []
        
        for i, chunk in enumerate(chunks, 1):
            source = chunk.metadata.get("metadata", {}).get("filename", f"مصدر {i}")
            context_parts.append(f"[{i}] {source}:")
            context_parts.append(chunk.text)
            context_parts.append("")
        
        return "\n".join(context_parts)
    
    # ============================================================
    # طرق حساب الثقة
    # ============================================================
    
    def _calculate_confidence(
        self,
        documents: List[Dict[str, Any]],
        answer_length: int,
        chunks_used: int
    ) -> float:
        """
        حساب درجة الثقة في الإجابة
        
        Args:
            documents: المستندات المستخدمة
            answer_length: طول الإجابة
            chunks_used: عدد القطع المستخدمة
            
        Returns:
            درجة الثقة (0-1)
        """
        if not documents:
            return 0.0
        
        # 1. متوسط درجة المطابقة
        avg_relevance = sum(
            doc.get("relevance_score", 0.0) for doc in documents
        ) / len(documents)
        
        # 2. عدد المستندات المستخدمة
        doc_score = min(chunks_used / 5, 1.0)  # 5 مستندات كحد أقصى للثقة
        
        # 3. طول الإجابة
        length_score = min(answer_length / 200, 1.0)  # 200 حرف كحد أقصى
        
        # 4. وجود مستندات
        has_docs_score = 1.0 if chunks_used > 0 else 0.0
        
        # الوزن النهائي
        confidence = (
            avg_relevance * 0.5 +      # 50% من درجة المطابقة
            doc_score * 0.2 +          # 20% من عدد المستندات
            length_score * 0.2 +       # 20% من طول الإجابة
            has_docs_score * 0.1       # 10% من وجود مستندات
        )
        
        return min(max(confidence, 0.0), 1.0)
    
    # ============================================================
    # طرق تحسين الأسئلة
    # ============================================================
    
    def _enhance_question(self, question: str) -> str:
        """
        تحسين السؤال لتحسين جودة الاسترجاع
        
        Args:
            question: السؤال الأصلي
            
        Returns:
            السؤال المحسن
        """
        # إزالة علامات الترقيم الزائدة
        question = question.strip()
        
        # إذا كان السؤال قصيراً، حاول توسيعه
        if len(question.split()) < 3:
            # إضافة كلمات مفتاحية عامة
            question = f"{question} معلومات تفاصيل"
        
        return question
    
    def _extract_keywords(self, question: str) -> List[str]:
        """
        استخراج الكلمات المفتاحية من السؤال
        
        Args:
            question: السؤال
            
        Returns:
            قائمة الكلمات المفتاحية
        """
        # كلمات شائعة في المشتريات
        procurement_keywords = [
            "عقد", "مورد", "توريد", "شراء", "طلب", "فاتورة",
            "جودة", "تقييم", "سعر", "تكلفة", "ميزانية",
            "شروط", "بنود", "التزام", "ضمان", "تسليم",
            "منتج", "خدمة", "مواد", "معدات", "تخزين"
        ]
        
        words = question.split()
        keywords = []
        
        for word in words:
            # إزالة علامات الترقيم
            clean_word = word.strip("،؛؟!.،")
            if clean_word in procurement_keywords:
                keywords.append(clean_word)
        
        return keywords
    
    # ============================================================
    # طرق تنسيق النتائج
    # ============================================================
    
    def _format_sources(self, documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        تنسيق المصادر للعرض
        
        Args:
            documents: قائمة المستندات
            
        Returns:
            قائمة المصادر المنسقة
        """
        sources = []
        
        for doc in documents:
            metadata = doc.get("metadata", {})
            
            source = {
                "id": doc.get("id", ""),
                "filename": metadata.get("filename", "مصدر غير معروف"),
                "category": metadata.get("category", "غير مصنف"),
                "content": doc.get("text", ""),
                "relevance_score": doc.get("relevance_score", 0.0),
                "preview": self._get_preview(doc.get("text", ""))
            }
            
            # إضافة معلومات إضافية حسب التصنيف
            if metadata.get("category") == "contracts":
                source["contract_value"] = metadata.get("contract_value")
                source["supplier"] = metadata.get("supplier")
            elif metadata.get("category") == "quality_reports":
                source["quality_score"] = metadata.get("quality_score")
                source["supplier"] = metadata.get("supplier")
            elif metadata.get("category") == "quotations":
                source["quotation_value"] = metadata.get("quotation_value")
                source["supplier"] = metadata.get("supplier")
            elif metadata.get("category") == "policies":
                source["policy_type"] = metadata.get("policy_type")
            
            sources.append(source)
        
        return sources
    
    def _get_preview(self, text: str, max_length: int = 150) -> str:
        """
        الحصول على معاينة للنص
        
        Args:
            text: النص الكامل
            max_length: الحد الأقصى لطول المعاينة
            
        Returns:
            معاينة النص
        """
        if len(text) <= max_length:
            return text
        
        # قطع عند أقرب مسافة
        preview = text[:max_length]
        last_space = preview.rfind(' ')
        
        if last_space > 0:
            preview = preview[:last_space]
        
        return preview + "..."
    
    # ============================================================
    # طرق مساعدة
    # ============================================================
    
    async def answer_batch(
        self,
        questions: List[str],
        **kwargs
    ) -> List[QAResult]:
        """
        الإجابة على مجموعة من الأسئلة
        
        Args:
            questions: قائمة الأسئلة
            **kwargs: معاملات إضافية
            
        Returns:
            قائمة النتائج
        """
        results = []
        
        for question in questions:
            result = await self.answer(question, **kwargs)
            results.append(result)
        
        return results
    
    async def answer_with_feedback(
        self,
        question: str,
        feedback: str,
        **kwargs
    ) -> QAResult:
        """
        الإجابة مع ملاحظات المستخدم
        
        Args:
            question: السؤال
            feedback: ملاحظات المستخدم
            **kwargs: معاملات إضافية
            
        Returns:
            نتيجة السؤال
        """
        # إضافة الملاحظات إلى السؤال
        enhanced_question = f"{question}\nملاحظات: {feedback}"
        
        return await self.answer(enhanced_question, **kwargs)
    
    def get_stats(self) -> Dict[str, Any]:
        """
        الحصول على إحصائيات المحرك
        
        Returns:
            إحصائيات المحرك
        """
        return {
            "retriever_stats": self.retriever.get_stats(),
            "reranker_stats": self.reranker.get_stats(),
            "default_top_k": self.default_top_k,
            "default_max_sources": self.default_max_sources,
            "min_confidence": self.min_confidence
        }
    
    def reset(self) -> None:
        """
        إعادة تعيين المحرك
        """
        self.retriever.reset()
        self.reranker.reset()
        logger.info("🔄 QA Engine reset")
    
    def get_system_prompt(self, context: str) -> str:
        """
        الحصول على النظام الموجه للـ LLM
        
        Args:
            context: السياق
            
        Returns:
            النظام الموجه
        """
        return RAG_PROMPTS["system"].format(context=context)
