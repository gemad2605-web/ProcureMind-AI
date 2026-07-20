# backend/app/services/chat_service.py
"""
💬 خدمة المحادثة - Chat Service

تدير منطق المحادثة بالكامل:
- استقبال الأسئلة
- تنفيذ RAG
- توليد الإجابات
- إدارة سجل المحادثات
"""

from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import uuid
import asyncio

from app.rag.qa_engine import QAEngine
from app.rag.retriever import Retriever
from app.rag.reranker import Reranker
from app.llm.grok_client import GrokClient
from app.llm.llm_factory import LLMFactory
from app.core.config import settings
from app.core.prompts import get_rag_prompt, get_system_prompt
from app.utils.logger import logger


class ChatService:
    """
    خدمة المحادثة
    
    تدير:
    - محادثات المستخدمين
    - تنفيذ RAG
    - سجل المحادثات
    - إدارة الجلسات
    """
    
    def __init__(
        self,
        qa_engine: Optional[QAEngine] = None,
        retriever: Optional[Retriever] = None,
        reranker: Optional[Reranker] = None,
        llm_client: Optional[GrokClient] = None,
        max_history: int = 50
    ):
        """
        تهيئة خدمة المحادثة
        
        Args:
            qa_engine: محرك RAG
            retriever: أداة الاسترجاع
            reranker: أداة إعادة الترتيب
            llm_client: عميل النموذج اللغوي
            max_history: الحد الأقصى لسجل المحادثة
        """
        # تهيئة المكونات
        self.retriever = retriever or Retriever()
        self.reranker = reranker or Reranker()
        self.llm_factory = LLMFactory()
        
        # استخدام LLM المقدم أو إنشاء واحد
        if llm_client:
            self.llm_client = llm_client
        else:
            self.llm_client = self.llm_factory.get_default_client()
        
        # إنشاء محرك RAG
        self.qa_engine = qa_engine or QAEngine(
            retriever=self.retriever,
            reranker=self.reranker,
            llm=self.llm_client
        )
        
        # إعدادات الخدمة
        self.max_history = max_history
        
        # تخزين المحادثات (في الذاكرة - يمكن استبدالها بقاعدة بيانات)
        self.conversations: Dict[str, List[Dict[str, Any]]] = {}
        
        # إحصائيات
        self.stats = {
            "total_conversations": 0,
            "total_messages": 0,
            "total_questions": 0
        }
        
        logger.info("💬 ChatService initialized")
    
    # ============================================================
    # الطرق الرئيسية
    # ============================================================
    
    async def process_question(
        self,
        question: str,
        session_id: Optional[str] = None,
        max_sources: int = 5,
        temperature: float = 0.7,
        include_sources: bool = True,
        filter_category: Optional[str] = None,
        filter_supplier: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        معالجة سؤال المستخدم
        
        Args:
            question: سؤال المستخدم
            session_id: معرف الجلسة (ينشأ جديد إذا لم يتم توفيره)
            max_sources: عدد المصادر
            temperature: درجة الإبداع
            include_sources: عرض المصادر
            filter_category: تصفية حسب التصنيف
            filter_supplier: تصفية حسب المورد
            
        Returns:
            الرد مع المصادر
        """
        logger.info(f"💬 Processing question: {question[:50]}...")
        
        # 1. إنشاء أو استرجاع الجلسة
        if not session_id:
            session_id = str(uuid.uuid4())
        
        # 2. إضافة سؤال المستخدم إلى السجل
        user_message = {
            "role": "user",
            "content": question,
            "timestamp": datetime.now().isoformat()
        }
        self._add_message(session_id, user_message)
        
        # 3. تنفيذ RAG
        try:
            # الحصول على السياق من المحادثة السابقة
            context = self._get_conversation_context(session_id, max_messages=3)
            
            # إضافة السياق إلى kwargs
            kwargs["context"] = context
            
            # تنفيذ RAG
            result = await self.qa_engine.answer(
                question=question,
                top_k=max_sources * 2,
                max_sources=max_sources,
                temperature=temperature,
                include_sources=include_sources,
                filter_category=filter_category,
                filter_supplier=filter_supplier,
                **kwargs
            )
            
            # 4. إضافة رد المساعد إلى السجل
            assistant_message = {
                "role": "assistant",
                "content": result.answer,
                "sources": result.sources,
                "confidence_score": result.confidence_score,
                "timestamp": datetime.now().isoformat()
            }
            self._add_message(session_id, assistant_message)
            
            # 5. تحديث الإحصائيات
            self.stats["total_questions"] += 1
            
            # 6. إرجاع النتيجة
            return {
                "answer": result.answer,
                "sources": result.sources if include_sources else [],
                "session_id": session_id,
                "question_id": str(uuid.uuid4()),
                "timestamp": datetime.now().isoformat(),
                "confidence_score": result.confidence_score,
                "processing_time": result.processing_time,
                "total_documents": result.retrieved_count,
                "retrieved_count": result.reranked_count
            }
            
        except Exception as e:
            logger.error(f"❌ Error processing question: {str(e)}")
            
            # إضافة رسالة خطأ إلى السجل
            error_message = {
                "role": "assistant",
                "content": f"❌ حدث خطأ: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
            self._add_message(session_id, error_message)
            
            raise
    
    async def process_question_with_stream(
        self,
        question: str,
        session_id: Optional[str] = None,
        **kwargs
    ):
        """
        معالجة سؤال مع تدفق الرد
        
        Args:
            question: سؤال المستخدم
            session_id: معرف الجلسة
            
        Yields:
            أجزاء الرد بشكل تدريجي
        """
        logger.info(f"💬 Processing question with stream: {question[:50]}...")
        
        # إنشاء الجلسة
        if not session_id:
            session_id = str(uuid.uuid4())
        
        # إضافة سؤال المستخدم
        user_message = {
            "role": "user",
            "content": question,
            "timestamp": datetime.now().isoformat()
        }
        self._add_message(session_id, user_message)
        
        try:
            # تنفيذ RAG مع تدفق
            # (هذا يتطلب تعديل في QAEngine لدعم التدفق)
            result = await self.qa_engine.answer(
                question=question,
                **kwargs
            )
            
            # تقسيم الرد إلى أجزاء
            answer = result.answer
            words = answer.split()
            
            for i, word in enumerate(words):
                yield f"{word} "
                await asyncio.sleep(0.02)  # محاكاة التدفق
            
            # إضافة الرد إلى السجل
            assistant_message = {
                "role": "assistant",
                "content": answer,
                "sources": result.sources,
                "timestamp": datetime.now().isoformat()
            }
            self._add_message(session_id, assistant_message)
            
            # إرسال المصادر في النهاية
            if kwargs.get("include_sources", True):
                yield f"\n\n📎 المصادر: {', '.join([s.get('filename', '') for s in result.sources])}"
            
        except Exception as e:
            logger.error(f"❌ Error in stream: {str(e)}")
            yield f"❌ حدث خطأ: {str(e)}"
    
    # ============================================================
    # طرق إدارة سجل المحادثة
    # ============================================================
    
    def _add_message(self, session_id: str, message: Dict[str, Any]) -> None:
        """
        إضافة رسالة إلى سجل المحادثة
        
        Args:
            session_id: معرف الجلسة
            message: الرسالة
        """
        if session_id not in self.conversations:
            self.conversations[session_id] = []
            self.stats["total_conversations"] += 1
        
        self.conversations[session_id].append(message)
        self.stats["total_messages"] += 1
        
        # تطبيق الحد الأقصى للسجل
        if len(self.conversations[session_id]) > self.max_history:
            self.conversations[session_id] = self.conversations[session_id][-self.max_history:]
    
    def _get_conversation_context(
        self,
        session_id: str,
        max_messages: int = 3
    ) -> str:
        """
        الحصول على سياق المحادثة السابقة
        
        Args:
            session_id: معرف الجلسة
            max_messages: عدد الرسائل السابقة
            
        Returns:
            سياق المحادثة
        """
        if session_id not in self.conversations:
            return ""
        
        messages = self.conversations[session_id]
        
        # الحصول على آخر الرسائل
        recent = messages[-max_messages * 2:] if len(messages) > max_messages * 2 else messages
        
        # بناء السياق
        context_parts = []
        for msg in recent:
            role = "المستخدم" if msg["role"] == "user" else "المساعد"
            content = msg.get("content", "")
            context_parts.append(f"{role}: {content}")
        
        return "\n".join(context_parts)
    
    def get_conversation(self, session_id: str) -> List[Dict[str, Any]]:
        """
        الحصول على سجل محادثة
        
        Args:
            session_id: معرف الجلسة
            
        Returns:
            قائمة الرسائل
        """
        return self.conversations.get(session_id, [])
    
    def get_conversation_history(
        self,
        session_id: str,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        الحصول على سجل المحادثة مع تحديد العدد
        
        Args:
            session_id: معرف الجلسة
            limit: عدد الرسائل
            
        Returns:
            قائمة الرسائل
        """
        messages = self.conversations.get(session_id, [])
        if limit:
            return messages[-limit:]
        return messages
    
    def clear_conversation(self, session_id: str) -> bool:
        """
        مسح سجل المحادثة
        
        Args:
            session_id: معرف الجلسة
            
        Returns:
            نجاح المسح
        """
        if session_id in self.conversations:
            self.conversations[session_id] = []
            logger.info(f"🗑️ Conversation cleared: {session_id}")
            return True
        return False
    
    def delete_conversation(self, session_id: str) -> bool:
        """
        حذف محادثة بالكامل
        
        Args:
            session_id: معرف الجلسة
            
        Returns:
            نجاح الحذف
        """
        if session_id in self.conversations:
            del self.conversations[session_id]
            logger.info(f"🗑️ Conversation deleted: {session_id}")
            return True
        return False
    
    # ============================================================
    # طرق إضافية
    # ============================================================
    
    async def get_suggested_questions(self, limit: int = 6) -> List[Dict[str, Any]]:
        """
        الحصول على أسئلة مقترحة
        
        Args:
            limit: عدد الأسئلة
            
        Returns:
            قائمة الأسئلة المقترحة
        """
        suggestions = [
            {
                "question": "ما هي شروط عقد Alpha Inc؟",
                "category": "contracts",
                "tags": ["عقد", "شروط", "مورد"]
            },
            {
                "question": "مين أفضل مورد حسب تقارير الجودة؟",
                "category": "quality_reports",
                "tags": ["جودة", "تقييم", "مورد"]
            },
            {
                "question": "إيه سياسة تقييم الموردين؟",
                "category": "policies",
                "tags": ["سياسة", "تقييم", "موردين"]
            },
            {
                "question": "قارن بين عروض أسعار Alpha Inc و Beta Supplies",
                "category": "quotations",
                "tags": ["عروض", "أسعار", "مقارنة"]
            },
            {
                "question": "ما هي قيمة عقد Gamma Co؟",
                "category": "contracts",
                "tags": ["عقد", "قيمة", "مورد"]
            },
            {
                "question": "تقرير جودة Delta Logistics",
                "category": "quality_reports",
                "tags": ["جودة", "تقرير", "خدمات"]
            },
            {
                "question": "إجراءات الشراء في المؤسسة",
                "category": "policies",
                "tags": ["شراء", "إجراءات", "مشتريات"]
            },
            {
                "question": "كم عدد الموردين المسجلين؟",
                "category": "suppliers",
                "tags": ["موردين", "إحصائيات"]
            }
        ]
        
        return suggestions[:limit]
    
    def get_stats(self) -> Dict[str, Any]:
        """
        الحصول على إحصائيات الخدمة
        
        Returns:
            إحصائيات الخدمة
        """
        return {
            **self.stats,
            "active_conversations": len(self.conversations),
            "max_history": self.max_history
        }
    
    def reset_stats(self) -> None:
        """إعادة تعيين الإحصائيات"""
        self.stats = {
            "total_conversations": 0,
            "total_messages": 0,
            "total_questions": 0
        }
        logger.info("🔄 ChatService stats reset")
    
    def get_all_sessions(self) -> List[str]:
        """
        الحصول على جميع معرفات الجلسات
        
        Returns:
            قائمة معرفات الجلسات
        """
        return list(self.conversations.keys())
    
    def get_conversation_count(self) -> int:
        """
        الحصول على عدد المحادثات
        
        Returns:
            عدد المحادثات
        """
        return len(self.conversations)
    
    def get_message_count(self) -> int:
        """
        الحصول على عدد الرسائل
        
        Returns:
            عدد الرسائل
        """
        total = 0
        for messages in self.conversations.values():
            total += len(messages)
        return total
    
    # ============================================================
    # طرق التنظيف
    # ============================================================
    
    def cleanup_old_conversations(self, max_age_days: int = 30) -> int:
        """
        تنظيف المحادثات القديمة
        
        Args:
            max_age_days: الحد الأقصى للعمر بالأيام
            
        Returns:
            عدد المحادثات المحذوفة
        """
        # هذه الطريقة تتطلب تخزين تاريخ المحادثة
        # في التنفيذ الحالي يتم تخزينها في الذاكرة فقط
        # يمكن توسيعها لاستخدام قاعدة بيانات
        logger.info("🧹 Cleanup old conversations not implemented (in-memory only)")
        return 0
