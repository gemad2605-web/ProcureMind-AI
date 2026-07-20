# backend/tests/test_chat.py
"""
🧪 اختبارات نقاط نهاية المحادثة (Chat Endpoints)
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch, AsyncMock
import json
from datetime import datetime

# استيراد التطبيق
from app.main import app
from app.api.chat import ChatRequest, ChatResponse

# إنشاء عميل اختبار
client = TestClient(app)


# ============================================================
# 1. اختبارات نقطة نهاية /chat
# ============================================================

class TestChatEndpoint:
    """اختبارات نقطة نهاية المحادثة"""
    
    def test_chat_success(self):
        """
        ✅ اختبار: المحادثة تعمل بنجاح
        """
        # بيانات الطلب
        payload = {
            "question": "ما هي شروط عقد Alpha Inc؟",
            "max_sources": 3,
            "temperature": 0.7
        }
        
        # إرسال الطلب
        response = client.post("/api/chat", json=payload)
        
        # التحقق من الاستجابة
        assert response.status_code == 200
        data = response.json()
        
        # التحقق من وجود الحقول المطلوبة
        assert "answer" in data
        assert "sources" in data
        assert "session_id" in data
        assert "question_id" in data
        assert "timestamp" in data
        
        # التحقق من أن الإجابة ليست فارغة
        assert len(data["answer"]) > 0
        
        # التحقق من أن المصادر قائمة
        assert isinstance(data["sources"], list)
    
    def test_chat_empty_question(self):
        """
        ❌ اختبار: سؤال فارغ
        """
        payload = {
            "question": "",
            "max_sources": 3
        }
        
        response = client.post("/api/chat", json=payload)
        
        # يجب أن يعيد خطأ 400
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
    
    def test_chat_very_long_question(self):
        """
        ❌ اختبار: سؤال طويل جداً
        """
        long_question = "أ" * 2000  # 2000 حرف
        
        payload = {
            "question": long_question,
            "max_sources": 3
        }
        
        response = client.post("/api/chat", json=payload)
        
        # يجب أن يعيد خطأ 400
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
    
    def test_chat_with_session_id(self):
        """
        ✅ اختبار: محادثة مع session_id
        """
        payload = {
            "question": "ما هي سياسة المشتريات؟",
            "session_id": "test-session-123",
            "max_sources": 5
        }
        
        response = client.post("/api/chat", json=payload)
        
        assert response.status_code == 200
        data = response.json()
        
        # التحقق من أن session_id هو نفسه المرسل
        assert data["session_id"] == "test-session-123"
    
    def test_chat_with_filters(self):
        """
        ✅ اختبار: محادثة مع تصفية
        """
        payload = {
            "question": "ما هي العقود النشطة؟",
            "filter_category": "contracts",
            "filter_supplier": "Alpha Inc",
            "max_sources": 5
        }
        
        response = client.post("/api/chat", json=payload)
        
        assert response.status_code == 200
        data = response.json()
        
        # التحقق من وجود إجابة
        assert "answer" in data
        assert len(data["answer"]) > 0
    
    def test_chat_with_include_sources_false(self):
        """
        ✅ اختبار: محادثة بدون مصادر
        """
        payload = {
            "question": "ما هي قيمة عقد Gamma Co؟",
            "include_sources": False,
            "max_sources": 3
        }
        
        response = client.post("/api/chat", json=payload)
        
        assert response.status_code == 200
        data = response.json()
        
        # المصادر يجب أن تكون فارغة
        assert len(data["sources"]) == 0


# ============================================================
# 2. اختبارات نقطة نهاية /chat/stream
# ============================================================

class TestChatStreamEndpoint:
    """اختبارات نقطة نهاية التدفق"""
    
    def test_chat_stream_success(self):
        """
        ✅ اختبار: التدفق يعمل بنجاح
        """
        payload = {
            "question": "قارن بين عروض Alpha Inc و Beta Supplies",
            "max_sources": 3
        }
        
        # إرسال طلب تدفق
        with client.stream("POST", "/api/chat/stream", json=payload) as response:
            assert response.status_code == 200
            
            # تجميع البيانات
            chunks = []
            for chunk in response.iter_text():
                if chunk.startswith("data: "):
                    chunks.append(chunk[6:])
            
            # التحقق من وجود بيانات
            assert len(chunks) > 0
            
            # التحقق من وجود [DONE]
            assert any("[DONE]" in chunk for chunk in chunks)
    
    def test_chat_stream_error(self):
        """
        ❌ اختبار: التدفق مع خطأ
        """
        payload = {
            "question": "",  # سؤال فارغ - يجب أن يعطي خطأ
            "max_sources": 3
        }
        
        with client.stream("POST", "/api/chat/stream", json=payload) as response:
            assert response.status_code == 400


# ============================================================
# 3. اختبارات نقطة نهاية /chat/history
# ============================================================

class TestChatHistoryEndpoint:
    """اختبارات سجل المحادثة"""
    
    def test_get_history_success(self):
        """
        ✅ اختبار: جلب سجل المحادثة بنجاح
        """
        # أولاً: إنشاء محادثة
        chat_payload = {
            "question": "ما هي سياسة تقييم الموردين؟",
            "session_id": "history-test-123"
        }
        client.post("/api/chat", json=chat_payload)
        
        # ثانياً: جلب السجل
        response = client.get("/api/chat/history/history-test-123")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["session_id"] == "history-test-123"
        assert "history" in data
        assert isinstance(data["history"], list)
    
    def test_get_history_not_found(self):
        """
        ❌ اختبار: سجل غير موجود
        """
        response = client.get("/api/chat/history/non-existent-session")
        
        # يجب أن يعيد خطأ 404 أو 500
        assert response.status_code in [404, 500]
    
    def test_delete_history_success(self):
        """
        ✅ اختبار: حذف سجل المحادثة بنجاح
        """
        # أولاً: إنشاء محادثة
        chat_payload = {
            "question": "ما هي قيمة عقد Delta Logistics؟",
            "session_id": "delete-test-123"
        }
        client.post("/api/chat", json=chat_payload)
        
        # ثانياً: حذف السجل
        response = client.delete("/api/chat/history/delete-test-123")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["message"] is not None
        assert data["session_id"] == "delete-test-123"


# ============================================================
# 4. اختبارات نقطة نهاية /chat/suggestions
# ============================================================

class TestChatSuggestionsEndpoint:
    """اختبارات الأسئلة المقترحة"""
    
    def test_get_suggestions_success(self):
        """
        ✅ اختبار: جلب الأسئلة المقترحة بنجاح
        """
        response = client.get("/api/chat/suggestions")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "suggestions" in data
        assert isinstance(data["suggestions"], list)
        assert data["count"] > 0
        
        # التحقق من هيكل الاقتراح
        if len(data["suggestions"]) > 0:
            suggestion = data["suggestions"][0]
            assert "question" in suggestion
            assert "category" in suggestion
            assert "tags" in suggestion


# ============================================================
# 5. اختبارات نماذج البيانات (Schemas)
# ============================================================

class TestChatSchemas:
    """اختبارات نماذج البيانات"""
    
    def test_chat_request_schema(self):
        """
        ✅ اختبار: نموذج طلب المحادثة
        """
        # نموذج صحيح
        request = ChatRequest(
            question="ما هي شروط العقد؟",
            max_sources=5,
            temperature=0.7
        )
        
        assert request.question == "ما هي شروط العقد؟"
        assert request.max_sources == 5
        assert request.temperature == 0.7
    
    def test_chat_request_invalid_max_sources(self):
        """
        ❌ اختبار: max_sources غير صحيح
        """
        with pytest.raises(ValueError):
            request = ChatRequest(
                question="ما هي شروط العقد؟",
                max_sources=20  # أكبر من 10
            )
    
    def test_chat_request_invalid_temperature(self):
        """
        ❌ اختبار: temperature غير صحيح
        """
        with pytest.raises(ValueError):
            request = ChatRequest(
                question="ما هي شروط العقد؟",
                temperature=1.5  # أكبر من 1.0
            )
    
    def test_chat_response_schema(self):
        """
        ✅ اختبار: نموذج استجابة المحادثة
        """
        response = ChatResponse(
            answer="هذه هي الإجابة...",
            sources=[],
            session_id="test-123",
            question_id="q-456",
            timestamp=datetime.now().isoformat()
        )
        
        assert response.answer == "هذه هي الإجابة..."
        assert response.session_id == "test-123"
        assert response.question_id == "q-456"


# ============================================================
# 6. اختبارات الأداء
# ============================================================

class TestChatPerformance:
    """اختبارات أداء المحادثة"""
    
    def test_chat_response_time(self):
        """
        ⏱️ اختبار: زمن استجابة المحادثة
        """
        import time
        
        payload = {
            "question": "ما هي شروط عقد Beta Supplies؟",
            "max_sources": 3
        }
        
        start_time = time.time()
        response = client.post("/api/chat", json=payload)
        end_time = time.time()
        
        response_time = end_time - start_time
        
        assert response.status_code == 200
        # يجب أن يكون زمن الاستجابة أقل من 10 ثواني
        assert response_time < 10.0, f"Response time: {response_time} seconds"
    
    def test_chat_concurrent_requests(self):
        """
        🔄 اختبار: طلبات متزامنة
        """
        import concurrent.futures
        
        def send_request():
            payload = {
                "question": "ما هي سياسة المشتريات؟",
                "max_sources": 3
            }
            return client.post("/api/chat", json=payload)
        
        # إرسال 5 طلبات متزامنة
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(send_request) for _ in range(5)]
            results = [f.result() for f in futures]
        
        # التحقق من أن جميع الطلبات نجحت
        for response in results:
            assert response.status_code == 200
            data = response.json()
            assert "answer" in data


# ============================================================
# 7. اختبارات الأمان
# ============================================================

class TestChatSecurity:
    """اختبارات أمان المحادثة"""
    
    def test_chat_sql_injection(self):
        """
        🔒 اختبار: حقن SQL
        """
        payload = {
            "question": "'; DROP TABLE users; --",
            "max_sources": 3
        }
        
        response = client.post("/api/chat", json=payload)
        
        # يجب أن يعالج الطلب بشكل آمن (لا يسمح بالحقن)
        assert response.status_code == 200
        data = response.json()
        assert "answer" in data
    
    def test_chat_xss_attack(self):
        """
        🔒 اختبار: هجوم XSS
        """
        payload = {
            "question": "<script>alert('XSS')</script>",
            "max_sources": 3
        }
        
        response = client.post("/api/chat", json=payload)
        
        # يجب أن يعالج الطلب بشكل آمن
        assert response.status_code == 200
        data = response.json()
        assert "answer" in data
    
    def test_chat_large_payload(self):
        """
        🔒 اختبار: حمولة كبيرة جداً
        """
        large_payload = {
            "question": "أ" * 10000,  # 10,000 حرف
            "max_sources": 10
        }
        
        response = client.post("/api/chat", json=large_payload)
        
        # يجب أن يرفض أو يعالج
        assert response.status_code in [400, 413, 200]


# ============================================================
# 8. اختبارات التكامل (Integration)
# ============================================================

class TestChatIntegration:
    """اختبارات التكامل"""
    
    def test_full_chat_flow(self):
        """
        🔄 اختبار: تدفق المحادثة الكامل
        """
        # 1. بدء محادثة جديدة
        session_id = "integration-test-123"
        
        # 2. إرسال سؤال
        payload1 = {
            "question": "ما هي شروط عقد Alpha Inc؟",
            "session_id": session_id
        }
        response1 = client.post("/api/chat", json=payload1)
        assert response1.status_code == 200
        data1 = response1.json()
        assert "answer" in data1
        
        # 3. إرسال سؤال متابعة
        payload2 = {
            "question": "ما هي قيمة العقد؟",
            "session_id": session_id
        }
        response2 = client.post("/api/chat", json=payload2)
        assert response2.status_code == 200
        data2 = response2.json()
        assert "answer" in data2
        
        # 4. جلب السجل
        history_response = client.get(f"/api/chat/history/{session_id}")
        assert history_response.status_code == 200
        
        # 5. التحقق من أن السجل يحتوي على سؤالين
        history_data = history_response.json()
        assert len(history_data["history"]) >= 2
    
    def test_chat_with_different_languages(self):
        """
        🌐 اختبار: لغات مختلفة
        """
        # اختبار بالعربية
        arabic_payload = {
            "question": "ما هي شروط عقد Alpha Inc؟",
            "max_sources": 3
        }
        arabic_response = client.post("/api/chat", json=arabic_payload)
        assert arabic_response.status_code == 200
        
        # اختبار بالإنجليزية
        english_payload = {
            "question": "What are the terms of Alpha Inc contract?",
            "max_sources": 3
        }
        english_response = client.post("/api/chat", json=english_payload)
        assert english_response.status_code == 200


# ============================================================
# 9. اختبارات Mock (محاكاة)
# ============================================================

class TestChatWithMocks:
    """اختبارات مع Mock"""
    
    @patch('app.services.chat_service.ChatService.process_question')
    def test_chat_with_mock_service(self, mock_process):
        """
        ✅ اختبار: استخدام Mock للخدمة
        """
        # إعداد الـ Mock
        mock_process.return_value = {
            "answer": "هذه إجابة اختبارية",
            "sources": [
                {
                    "id": "doc-1",
                    "filename": "test_doc.txt",
                    "category": "contracts",
                    "content": "محتوى اختبار",
                    "relevance_score": 0.95
                }
            ],
            "confidence_score": 0.9,
            "total_documents": 10
        }
        
        payload = {
            "question": "سؤال اختبار",
            "max_sources": 1
        }
        
        response = client.post("/api/chat", json=payload)
        
        assert response.status_code == 200
        data = response.json()
        assert data["answer"] == "هذه إجابة اختبارية"
        assert len(data["sources"]) == 1
        
        # التحقق من أن الـ Mock تم استدعاؤه
        mock_process.assert_called_once()


# ============================================================
# 10. اختبارات التحميل (Load Testing)
# ============================================================

@pytest.mark.skip(reason="Performance test - run manually")
class TestChatLoad:
    """اختبارات التحميل (تتطلب تشغيل يدوي)"""
    
    def test_load_test(self):
        """
        📊 اختبار: تحميل 100 طلب
        """
        import time
        import concurrent.futures
        
        def send_request(i):
            payload = {
                "question": f"سؤال اختبار رقم {i}",
                "max_sources": 3
            }
            return client.post("/api/chat", json=payload)
        
        start_time = time.time()
        
        # إرسال 100 طلب
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(send_request, i) for i in range(100)]
            results = [f.result() for f in futures]
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # حساب النجاحات
        success_count = sum(1 for r in results if r.status_code == 200)
        
        print(f"\n📊 نتائج اختبار التحميل:")
        print(f"   ✅ النجاح: {success_count}/100")
        print(f"   ⏱️  الوقت الإجمالي: {total_time:.2f} ثانية")
        print(f"   ⚡ متوسط الوقت: {total_time/100:.2f} ثانية لكل طلب")
        
        assert success_count >= 80  # 80% نجاح على الأقل
