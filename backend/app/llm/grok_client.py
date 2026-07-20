# backend/app/llm/grok_client.py
"""
🤖 عميل Grok API من xAI

يتواصل مع واجهة Grok API لتوليد الإجابات على الأسئلة
"""

import json
import time
from typing import Optional, Dict, Any, List
import httpx
from datetime import datetime

from app.core.config import settings
from app.utils.logger import logger


class GrokClient:
    """
    عميل Grok API
    
    يدعم:
    - توليد الإجابات
    - تدفق الإجابات (Streaming)
    - تحويل النص إلى كلام (اختياري)
    - متابعة المحادثات
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        api_url: Optional[str] = None,
        model: Optional[str] = None,
        timeout: int = 60
    ):
        """
        تهيئة عميل Grok
        
        Args:
            api_key: مفتاح API (يؤخذ من الإعدادات إذا لم يتم توفيره)
            api_url: رابط API (يؤخذ من الإعدادات إذا لم يتم توفيره)
            model: اسم النموذج (يؤخذ من الإعدادات إذا لم يتم توفيره)
            timeout: مهلة الطلب بالثواني
        """
        self.api_key = api_key or settings.GROK_API_KEY
        self.api_url = api_url or settings.GROK_API_URL
        self.model = model or settings.GROK_MODEL
        self.timeout = timeout
        
        # إحصائيات
        self.stats = {
            "total_requests": 0,
            "total_tokens": 0,
            "avg_response_time": 0,
            "last_request_time": 0
        }
        
        # إعدادات الطلب
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # التحقق من وجود المفتاح
        if not self.api_key or self.api_key == "":
            logger.warning("⚠️ GROK_API_KEY not set! Please set it in .env file")
        
        logger.info(f"🤖 Grok Client initialized with model: {self.model}")
    
    # ============================================================
    # الطريقة الرئيسية - توليد الإجابة
    # ============================================================
    
    async def generate(
        self,
        question: str,
        context: str = "",
        temperature: float = 0.7,
        max_tokens: int = 1000,
        system_prompt: Optional[str] = None,
        stream: bool = False,
        **kwargs
    ) -> str:
        """
        توليد إجابة باستخدام Grok API
        
        Args:
            question: سؤال المستخدم
            context: السياق (النصوص المسترجعة)
            temperature: درجة الإبداع (0-1)
            max_tokens: الحد الأقصى لعدد الرموز
            system_prompt: توجيه النظام (يؤخذ من الإعدادات إذا لم يتم توفيره)
            stream: تدفق الإجابة
            
        Returns:
            الإجابة النصية
        """
        start_time = time.time()
        
        logger.info(f"🤖 Generating response for: {question[:50]}...")
        
        # 1. التحقق من المفتاح
        if not self.api_key:
            error_msg = "❌ GROK_API_KEY not set. Please set it in .env file"
            logger.error(error_msg)
            return f"⚠️ {error_msg}"
        
        # 2. بناء الرسائل
        messages = self._build_messages(
            question=question,
            context=context,
            system_prompt=system_prompt
        )
        
        # 3. تجهيز الطلب
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": stream,
            **kwargs
        }
        
        try:
            # 4. إرسال الطلب
            if stream:
                response_text = await self._stream_request(payload)
            else:
                response_text = await self._sync_request(payload)
            
            # 5. تحديث الإحصائيات
            elapsed = time.time() - start_time
            self._update_stats(len(response_text), elapsed)
            
            logger.info(f"✅ Response generated in {elapsed:.2f}s")
            
            return response_text
            
        except Exception as e:
            logger.error(f"❌ Error generating response: {str(e)}")
            return f"❌ خطأ: {str(e)}"
    
    # ============================================================
    # طرق الطلب
    # ============================================================
    
    async def _sync_request(self, payload: Dict[str, Any]) -> str:
        """
        إرسال طلب عادي (غير متدفق)
        
        Args:
            payload: بيانات الطلب
            
        Returns:
            الإجابة النصية
        """
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                self.api_url,
                headers=self.headers,
                json=payload
            )
            
            # التحقق من الاستجابة
            if response.status_code != 200:
                error_msg = f"❌ API Error: {response.status_code} - {response.text}"
                logger.error(error_msg)
                return error_msg
            
            # استخراج الإجابة
            data = response.json()
            
            if "choices" in data and len(data["choices"]) > 0:
                return data["choices"][0]["message"]["content"]
            else:
                return "⚠️ لم يتم العثور على إجابة من النموذج"
    
    async def _stream_request(self, payload: Dict[str, Any]) -> str:
        """
        إرسال طلب مع تدفق
        
        Args:
            payload: بيانات الطلب
            
        Returns:
            الإجابة النصية الكاملة
        """
        full_response = ""
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            async with client.stream(
                "POST",
                self.api_url,
                headers=self.headers,
                json=payload
            ) as response:
                
                if response.status_code != 200:
                    error_msg = f"❌ API Error: {response.status_code}"
                    logger.error(error_msg)
                    return error_msg
                
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data_str = line[6:]
                        if data_str == "[DONE]":
                            break
                        
                        try:
                            data = json.loads(data_str)
                            if "choices" in data and len(data["choices"]) > 0:
                                delta = data["choices"][0].get("delta", {})
                                content = delta.get("content", "")
                                if content:
                                    full_response += content
                                    # طباعة أثناء التدفق (للاختبار)
                                    print(content, end="", flush=True)
                        except json.JSONDecodeError:
                            continue
        
        return full_response
    
    # ============================================================
    # طرق مساعدة
    # ============================================================
    
    def _build_messages(
        self,
        question: str,
        context: str,
        system_prompt: Optional[str] = None
    ) -> List[Dict[str, str]]:
        """
        بناء قائمة الرسائل للطلب
        
        Args:
            question: سؤال المستخدم
            context: السياق
            system_prompt: توجيه النظام
            
        Returns:
            قائمة الرسائل
        """
        messages = []
        
        # 1. توجيه النظام
        if system_prompt:
            messages.append({
                "role": "system",
                "content": system_prompt
            })
        else:
            # توجيه النظام الافتراضي
            messages.append({
                "role": "system",
                "content": self._get_default_system_prompt(context)
            })
        
        # 2. السياق (إذا كان موجوداً)
        if context and context.strip():
            messages.append({
                "role": "user",
                "content": f"المعلومات المتاحة:\n{context}\n\nالسؤال: {question}"
            })
        else:
            # إذا لم يكن هناك سياق
            messages.append({
                "role": "user",
                "content": f"{question}\n\nملاحظة: لا توجد معلومات كافية للإجابة على هذا السؤال."
            })
        
        return messages
    
    def _get_default_system_prompt(self, context: str) -> str:
        """
        الحصول على توجيه النظام الافتراضي
        
        Args:
            context: السياق
            
        Returns:
            توجيه النظام
        """
        # إذا كان هناك سياق
        if context and context.strip():
            return """أنت مساعد ذكي متخصص في مجال المشتريات وإدارة العقود.
المهمة: استخدم المعلومات المتاحة في السياق للإجابة على أسئلة المستخدم.
التعليمات:
1. أجب فقط بناءً على المعلومات الموجودة في السياق
2. إذا لم تجد المعلومة في السياق، قل ذلك بوضوح
3. كن دقيقاً ومختصراً في الإجابة
4. استخدم اللغة العربية الفصحى
5. إذا ذكرت أرقاماً، تأكد من دقتها
6. يمكنك تنظيم الإجابة في نقاط لتوضيح المعلومات
"""
        else:
            return """أنت مساعد ذكي متخصص في مجال المشتريات وإدارة العقود.
المهمة: أجب على أسئلة المستخدم بأفضل طريقة ممكنة.
التعليمات:
1. إذا لم تعرف الإجابة، قل ذلك بوضوح
2. كن دقيقاً ومختصراً
3. استخدم اللغة العربية الفصحى
4. اقترح على المستخدم توفير معلومات إضافية إذا لزم الأمر
"""
    
    def _update_stats(self, tokens: int, elapsed: float) -> None:
        """
        تحديث الإحصائيات
        
        Args:
            tokens: عدد الرموز
            elapsed: زمن المعالجة
        """
        self.stats["total_requests"] += 1
        self.stats["total_tokens"] += tokens
        self.stats["last_request_time"] = elapsed
        
        # تحديث المتوسط
        total = self.stats["total_requests"]
        if total > 0:
            self.stats["avg_response_time"] = (
                (self.stats["avg_response_time"] * (total - 1) + elapsed) / total
            )
    
    # ============================================================
    # طرق إضافية
    # ============================================================
    
    async def check_health(self) -> bool:
        """
        التحقق من صحة الاتصال بـ Grok API
        
        Returns:
            صحة الاتصال
        """
        if not self.api_key:
            return False
        
        try:
            # إرسال طلب اختبار بسيط
            test_response = await self.generate(
                question="Hello",
                context="",
                temperature=0.1,
                max_tokens=10
            )
            
            # التحقق من أن الاستجابة لا تحتوي على خطأ
            if not test_response.startswith("❌") and not test_response.startswith("⚠️"):
                logger.info("✅ Grok API health check passed")
                return True
            else:
                logger.warning(f"⚠️ Grok API health check failed: {test_response[:100]}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Grok API health check error: {str(e)}")
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """
        الحصول على إحصائيات العميل
        
        Returns:
            إحصائيات العميل
        """
        return {
            **self.stats,
            "model": self.model,
            "api_url": self.api_url,
            "timeout": self.timeout
        }
    
    def reset_stats(self) -> None:
        """إعادة تعيين الإحصائيات"""
        self.stats = {
            "total_requests": 0,
            "total_tokens": 0,
            "avg_response_time": 0,
            "last_request_time": 0
        }
        logger.info("🔄 Grok Client stats reset")
    
    def set_api_key(self, api_key: str) -> None:
        """
        تحديث مفتاح API
        
        Args:
            api_key: المفتاح الجديد
        """
        self.api_key = api_key
        self.headers["Authorization"] = f"Bearer {api_key}"
        logger.info("🔑 Grok API key updated")
    
    def set_model(self, model: str) -> None:
        """
        تحديث النموذج
        
        Args:
            model: اسم النموذج الجديد
        """
        self.model = model
        logger.info(f"🔄 Grok model updated to: {model}")
