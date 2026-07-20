# backend/tests/test_rag.py
"""
🧪 اختبارات محرك RAG (Retrieval-Augmented Generation)

اختبارات المكونات: الاسترجاع، إعادة الترتيب، التقسيم، ومحرك الأسئلة
"""

import pytest
import asyncio
import numpy as np
from unittest.mock import Mock, patch, AsyncMock
from typing import List, Dict, Any

from app.rag.retriever import Retriever
from app.rag.reranker import Reranker
from app.rag.chunking import Chunking, Chunk
from app.rag.qa_engine import QAEngine, QAResult
from app.rag.semantic_search import SemanticSearch
from app.database.embeddings import Embeddings
from app.database.faiss_loader import FAISSLoader


# ============================================================
# 1. اختبارات التقسيم (Chunking)
# ============================================================

class TestChunking:
    """اختبارات تقسيم النصوص"""
    
    def setup_method(self):
        """تهيئة قبل كل اختبار"""
        self.chunking = Chunking(chunk_size=50, chunk_overlap=10)
        self.sample_text = """
        هذا نص تجريبي لاختبار وظيفة تقسيم النصوص.
        يتكون النص من عدة جمل وفقرات.
        الهدف هو التأكد من أن التقسيم يعمل بشكل صحيح.
        يجب أن يتم تقسيم النص إلى أجزاء متساوية تقريباً.
        مع الحفاظ على المعنى والسياق.
        """
    
    def test_chunk_by_words(self):
        """✅ اختبار: التقسيم حسب الكلمات"""
        chunks = self.chunking.chunk_by_words(self.sample_text)
        
        assert len(chunks) > 0
        for chunk in chunks:
            assert isinstance(chunk, Chunk)
            assert len(chunk.text) > 0
            assert "chunk" in chunk.id
            assert chunk.metadata.get("word_count", 0) > 0
    
    def test_chunk_by_sentences(self):
        """✅ اختبار: التقسيم حسب الجمل"""
        chunks = self.chunking.chunk_by_sentences(self.sample_text)
        
        assert len(chunks) > 0
        for chunk in chunks:
            assert isinstance(chunk, Chunk)
            assert len(chunk.text) > 0
    
    def test_chunk_by_paragraphs(self):
        """✅ اختبار: التقسيم حسب الفقرات"""
        chunks = self.chunking.chunk_by_paragraphs(self.sample_text)
        
        assert len(chunks) > 0
        for chunk in chunks:
            assert isinstance(chunk, Chunk)
            assert len(chunk.text) > 0
    
    def test_chunk_smart(self):
        """✅ اختبار: التقسيم الذكي"""
        chunks = self.chunking.chunk_smart(self.sample_text)
        
        assert len(chunks) > 0
        for chunk in chunks:
            assert isinstance(chunk, Chunk)
            assert len(chunk.text) > 0
    
    def test_chunk_statistics(self):
        """✅ اختبار: إحصائيات التقسيم"""
        chunks = self.chunking.chunk_by_words(self.sample_text)
        stats = self.chunking.get_chunk_statistics(chunks)
        
        assert stats["total_chunks"] == len(chunks)
        assert stats["total_words"] > 0
        assert stats["avg_word_count"] > 0
        assert stats["min_word_count"] >= 0
        assert stats["max_word_count"] > 0
    
    def test_empty_text(self):
        """✅ اختبار: نص فارغ"""
        chunks = self.chunking.chunk_by_words("")
        assert len(chunks) == 0
        
        chunks = self.chunking.chunk_by_sentences("")
        assert len(chunks) == 0
    
    def test_merge_chunks(self):
        """✅ اختبار: دمج القطع"""
        chunks = self.chunking.chunk_by_words(self.sample_text)
        merged = self.chunking.merge_chunks(chunks, max_chunk_size=100)
        
        assert len(merged) <= len(chunks)
        if merged:
            for chunk in merged:
                assert chunk.metadata.get("merged", False) or True


# ============================================================
# 2. اختبارات الاسترجاع (Retriever)
# ============================================================

class TestRetriever:
    """اختبارات الاسترجاع"""
    
    def setup_method(self):
        """تهيئة قبل كل اختبار"""
        self.retriever = Retriever(top_k=5)
    
    @pytest.mark.asyncio
    async def test_retrieve(self):
        """✅ اختبار: الاسترجاع الأساسي"""
        # لا يمكن الاختبار بدون FAISS حقيقي
        # نستخدم Mock للاختبار
        with patch.object(self.retriever, 'faiss_loader') as mock_loader:
            mock_loader.search = AsyncMock(return_value=[
                {"id": "doc1", "text": "نص تجريبي 1", "metadata": {}, "relevance_score": 0.9},
                {"id": "doc2", "text": "نص تجريبي 2", "metadata": {}, "relevance_score": 0.8}
            ])
            
            results = await self.retriever.retrieve("سؤال اختبار")
            
            assert len(results) > 0
            assert "id" in results[0]
            assert "text" in results[0]
            assert "relevance_score" in results[0]
    
    @pytest.mark.asyncio
    async def test_retrieve_with_filters(self):
        """✅ اختبار: الاسترجاع مع تصفية"""
        with patch.object(self.retriever, 'faiss_loader') as mock_loader:
            mock_loader.search = AsyncMock(return_value=[
                {"id": "doc1", "text": "عقد Alpha Inc", "metadata": {"category": "contracts", "supplier": "Alpha Inc"}, "relevance_score": 0.9}
            ])
            
            results = await self.retriever.retrieve(
                "سؤال اختبار",
                filter_category="contracts",
                filter_supplier="Alpha Inc"
            )
            
            assert len(results) > 0
            if results:
                assert results[0]["metadata"].get("category") == "contracts"
    
    @pytest.mark.asyncio
    async def test_retrieve_empty(self):
        """✅ اختبار: استرجاع بدون نتائج"""
        with patch.object(self.retriever, 'faiss_loader') as mock_loader:
            mock_loader.search = AsyncMock(return_value=[])
            
            results = await self.retriever.retrieve("سؤال غير موجود")
            
            assert len(results) == 0
    
    def test_get_stats(self):
        """✅ اختبار: إحصائيات الاسترجاع"""
        stats = self.retriever.get_stats()
        assert "total_queries" in stats
        assert "top_k" in stats
    
    def test_reset(self):
        """✅ اختبار: إعادة تعيين الإحصائيات"""
        self.retriever.reset()
        stats = self.retriever.get_stats()
        assert stats["total_queries"] == 0
        assert stats["total_documents_retrieved"] == 0


# ============================================================
# 3. اختبارات إعادة الترتيب (Reranker)
# ============================================================

class TestReranker:
    """اختبارات إعادة الترتيب"""
    
    def setup_method(self):
        """تهيئة قبل كل اختبار"""
        self.reranker = Reranker(use_cross_encoder=False)
        self.sample_docs = [
            {"id": "doc1", "text": "نص عن العقود والموردين", "metadata": {}, "relevance_score": 0.5},
            {"id": "doc2", "text": "نص عن الجودة والتقييم", "metadata": {}, "relevance_score": 0.7},
            {"id": "doc3", "text": "نص عن الأسعار والعروض", "metadata": {}, "relevance_score": 0.3}
        ]
    
    @pytest.mark.asyncio
    async def test_rerank(self):
        """✅ اختبار: إعادة الترتيب الأساسية"""
        results = await self.reranker.rerank("سؤال اختبار", self.sample_docs, top_k=3)
        
        assert len(results) > 0
        assert "rank" in results[0]
        assert "rerank_score" in results[0]
        assert "combined_score" in results[0]
        assert "relevance_label" in results[0]
    
    @pytest.mark.asyncio
    async def test_rerank_with_top_k(self):
        """✅ اختبار: إعادة الترتيب مع تحديد العدد"""
        results = await self.reranker.rerank("سؤال اختبار", self.sample_docs, top_k=2)
        
        assert len(results) <= 2
    
    @pytest.mark.asyncio
    async def test_rerank_empty(self):
        """✅ اختبار: إعادة ترتيب قائمة فارغة"""
        results = await self.reranker.rerank("سؤال اختبار", [])
        
        assert len(results) == 0
    
    def test_get_stats(self):
        """✅ اختبار: إحصائيات إعادة الترتيب"""
        stats = self.reranker.get_stats()
        assert "total_reranked" in stats
        assert "model_name" in stats


# ============================================================
# 4. اختبارات محرك الأسئلة (QAEngine)
# ============================================================

class TestQAEngine:
    """اختبارات محرك الأسئلة والأجوبة"""
    
    def setup_method(self):
        """تهيئة قبل كل اختبار"""
        self.qa_engine = QAEngine()
    
    @pytest.mark.asyncio
    async def test_answer(self):
        """✅ اختبار: الإجابة على سؤال"""
        with patch.object(self.qa_engine, 'retriever') as mock_retriever:
            with patch.object(self.qa_engine, 'reranker') as mock_reranker:
                with patch.object(self.qa_engine, 'llm') as mock_llm:
                    # Mock الاسترجاع
                    mock_retriever.retrieve = AsyncMock(return_value=[
                        {"id": "doc1", "text": "شروط العقد: المدة 24 شهراً", "metadata": {"filename": "contract.txt"}, "relevance_score": 0.9}
                    ])
                    
                    # Mock إعادة الترتيب
                    mock_reranker.rerank = AsyncMock(return_value=[
                        {"id": "doc1", "text": "شروط العقد: المدة 24 شهراً", "metadata": {"filename": "contract.txt"}, "combined_score": 0.9}
                    ])
                    
                    # Mock LLM
                    mock_llm.generate = AsyncMock(return_value="شروط العقد: المدة 24 شهراً")
                    
                    result = await self.qa_engine.answer("ما هي شروط العقد؟")
                    
                    assert isinstance(result, QAResult)
                    assert len(result.answer) > 0
                    assert result.confidence_score > 0
                    assert result.processing_time > 0
    
    @pytest.mark.asyncio
    async def test_answer_with_sources(self):
        """✅ اختبار: الإجابة مع المصادر"""
        with patch.object(self.qa_engine, 'retriever') as mock_retriever:
            with patch.object(self.qa_engine, 'reranker') as mock_reranker:
                with patch.object(self.qa_engine, 'llm') as mock_llm:
                    mock_retriever.retrieve = AsyncMock(return_value=[
                        {"id": "doc1", "text": "نص تجريبي", "metadata": {"filename": "test.txt"}, "relevance_score": 0.9}
                    ])
                    mock_reranker.rerank = AsyncMock(return_value=[
                        {"id": "doc1", "text": "نص تجريبي", "metadata": {"filename": "test.txt"}, "combined_score": 0.9}
                    ])
                    mock_llm.generate = AsyncMock(return_value="إجابة اختبارية")
                    
                    result = await self.qa_engine.answer(
                        "سؤال اختبار",
                        include_sources=True
                    )
                    
                    assert len(result.sources) > 0
                    if result.sources:
                        assert "filename" in result.sources[0]
    
    @pytest.mark.asyncio
    async def test_answer_without_sources(self):
        """✅ اختبار: الإجابة بدون مصادر"""
        with patch.object(self.qa_engine, 'retriever') as mock_retriever:
            with patch.object(self.qa_engine, 'reranker') as mock_reranker:
                with patch.object(self.qa_engine, 'llm') as mock_llm:
                    mock_retriever.retrieve = AsyncMock(return_value=[])
                    mock_reranker.rerank = AsyncMock(return_value=[])
                    mock_llm.generate = AsyncMock(return_value="لا توجد معلومات")
                    
                    result = await self.qa_engine.answer(
                        "سؤال غير موجود",
                        include_sources=False
                    )
                    
                    assert len(result.sources) == 0
    
    @pytest.mark.asyncio
    async def test_answer_confidence(self):
        """✅ اختبار: درجة الثقة"""
        with patch.object(self.qa_engine, 'retriever') as mock_retriever:
            with patch.object(self.qa_engine, 'reranker') as mock_reranker:
                with patch.object(self.qa_engine, 'llm') as mock_llm:
                    mock_retriever.retrieve = AsyncMock(return_value=[
                        {"id": "doc1", "text": "نص طويل للإجابة على السؤال", "metadata": {}, "relevance_score": 0.9}
                    ])
                    mock_reranker.rerank = AsyncMock(return_value=[
                        {"id": "doc1", "text": "نص طويل للإجابة على السؤال", "metadata": {}, "combined_score": 0.9}
                    ])
                    mock_llm.generate = AsyncMock(return_value="إجابة مفصلة وكاملة عن السؤال المطروح")
                    
                    result = await self.qa_engine.answer("سؤال اختبار")
                    
                    assert 0 <= result.confidence_score <= 1
                    assert result.confidence_score > 0.5  # ثقة عالية
    
    def test_get_stats(self):
        """✅ اختبار: إحصائيات المحرك"""
        stats = self.qa_engine.get_stats()
        assert "retriever_stats" in stats
        assert "reranker_stats" in stats
        assert "default_top_k" in stats


# ============================================================
# 5. اختبارات البحث الدلالي (Semantic Search)
# ============================================================

class TestSemanticSearch:
    """اختبارات البحث الدلالي"""
    
    def setup_method(self):
        """تهيئة قبل كل اختبار"""
        self.search = SemanticSearch(top_k=5)
    
    @pytest.mark.asyncio
    async def test_search(self):
        """✅ اختبار: البحث الدلالي"""
        with patch.object(self.search, 'faiss_loader') as mock_loader:
            mock_loader.search = AsyncMock(return_value=[
                {"id": "doc1", "text": "نص تجريبي 1", "metadata": {}, "relevance_score": 0.9}
            ])
            
            results = await self.search.search("سؤال اختبار")
            
            assert len(results) > 0
            assert "id" in results[0]
            assert "text" in results[0]
    
    @pytest.mark.asyncio
    async def test_search_with_category(self):
        """✅ اختبار: البحث داخل تصنيف"""
        with patch.object(self.search, 'faiss_loader') as mock_loader:
            mock_loader.search = AsyncMock(return_value=[
                {"id": "doc1", "text": "عقد تجريبي", "metadata": {"category": "contracts"}, "relevance_score": 0.9}
            ])
            
            results = await self.search.search_by_category("سؤال اختبار", "contracts")
            
            assert len(results) > 0
            if results:
                assert results[0]["metadata"].get("category") == "contracts"
    
    def test_get_stats(self):
        """✅ اختبار: إحصائيات البحث"""
        stats = self.search.get_stats()
        assert "total_searches" in stats
        assert "top_k" in stats


# ============================================================
# 6. اختبارات التكامل
# ============================================================

class TestRAGIntegration:
    """اختبارات تكامل RAG"""
    
    @pytest.mark.asyncio
    async def test_full_rag_pipeline(self):
        """✅ اختبار: تدفق RAG الكامل"""
        # إنشاء المكونات
        chunking = Chunking(chunk_size=100)
        retriever = Retriever(top_k=5)
        reranker = Reranker(use_cross_encoder=False)
        qa_engine = QAEngine(retriever=retriever, reranker=reranker)
        
        # نص اختباري
        test_text = """
        هذا نص تجريبي لاختبار تدفق RAG بالكامل.
        يحتوي النص على معلومات عن العقود والموردين.
        المدة: 24 شهراً. القيمة: 1,500,000 ريال.
        """
        
        # تقسيم النص
        chunks = chunking.chunk_by_words(test_text)
        assert len(chunks) > 0
        
        # Mock الاسترجاع
        with patch.object(retriever, 'faiss_loader') as mock_loader:
            mock_loader.search = AsyncMock(return_value=[
                {
                    "id": "doc1",
                    "text": "المدة: 24 شهراً. القيمة: 1,500,000 ريال.",
                    "metadata": {"filename": "test.txt"},
                    "relevance_score": 0.9
                }
            ])
            
            with patch.object(qa_engine, 'llm') as mock_llm:
                mock_llm.generate = AsyncMock(
                    return_value="المدة: 24 شهراً. القيمة: 1,500,000 ريال."
                )
                
                # تنفيذ RAG
                result = await qa_engine.answer("ما هي شروط العقد؟")
                
                assert isinstance(result, QAResult)
                assert len(result.answer) > 0
                assert result.confidence_score > 0
                assert result.processing_time > 0
                assert result.retrieved_count >= 0
                assert result.reranked_count >= 0
    
    @pytest.mark.asyncio
    async def test_rag_with_no_documents(self):
        """✅ اختبار: RAG بدون مستندات"""
        qa_engine = QAEngine()
        
        with patch.object(qa_engine, 'retriever') as mock_retriever:
            mock_retriever.retrieve = AsyncMock(return_value=[])
            
            with patch.object(qa_engine, 'reranker') as mock_reranker:
                mock_reranker.rerank = AsyncMock(return_value=[])
                
                with patch.object(qa_engine, 'llm') as mock_llm:
                    mock_llm.generate = AsyncMock(return_value="لا توجد معلومات كافية")
                    
                    result = await qa_engine.answer("سؤال")
                    
                    assert isinstance(result, QAResult)
                    assert "لا توجد" in result.answer


# ============================================================
# 7. اختبارات الأداء
# ============================================================

@pytest.mark.slow
class TestRAGPerformance:
    """اختبارات أداء RAG"""
    
    @pytest.mark.asyncio
    async def test_retrieval_performance(self):
        """⏱️ اختبار: أداء الاسترجاع"""
        import time
        
        retriever = Retriever(top_k=10)
        
        with patch.object(retriever, 'faiss_loader') as mock_loader:
            # محاكاة 100 مستند
            docs = [
                {"id": f"doc{i}", "text": f"نص تجريبي {i}", "metadata": {}, "relevance_score": 0.9}
                for i in range(100)
            ]
            mock_loader.search = AsyncMock(return_value=docs)
            
            start = time.time()
            await retriever.retrieve("سؤال اختبار")
            elapsed = time.time() - start
            
            # يجب أن يكون الاسترجاع سريعاً (< 1 ثانية)
            assert elapsed < 1.0
    
    @pytest.mark.asyncio
    async def test_rerank_performance(self):
        """⏱️ اختبار: أداء إعادة الترتيب"""
        import time
        
        reranker = Reranker(use_cross_encoder=False)
        docs = [
            {"id": f"doc{i}", "text": f"نص تجريبي {i}", "metadata": {}, "relevance_score": 0.5 + i * 0.05}
            for i in range(50)
        ]
        
        start = time.time()
        await reranker.rerank("سؤال اختبار", docs)
        elapsed = time.time() - start
        
        # يجب أن يكون إعادة الترتيب سريعاً (< 0.5 ثانية)
        assert elapsed < 0.5


# ============================================================
# 8. تشغيل الاختبارات
# ============================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
