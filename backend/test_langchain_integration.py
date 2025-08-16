#!/usr/bin/env python3
"""
Test script để kiểm tra Langchain integration

Chạy script này để test:
- Langchain components initialization
- Vector store operations 
- RAG capabilities
- Tools integration
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.langchain_service import LangchainService
from services.knowledge_base_service import KnowledgeBaseService
from services.ai_service import AIService

def test_langchain_service():
    """Test LangchainService initialization và basic operations"""
    print("=" * 50)
    print("🧪 Testing LangchainService...")
    print("=" * 50)
    
    try:
        # Khởi tạo service
        langchain_service = LangchainService()
        
        # Test basic chat
        print("\n📝 Testing basic chat...")
        result = langchain_service.chat_with_rag(
            "Hello, can you explain what is Java programming?",
            []
        )
        print(f"Chat result: {result['success']}")
        if result['success']:
            print(f"Response preview: {result['answer'][:100]}...")
        
        # Test code processing
        print("\n🔧 Testing code processing...")
        code_result = langchain_service.process_code_with_langchain(
            task="comment_code",
            code="public class Hello { public static void main(String[] args) { System.out.println(\"Hello\"); } }",
            language="java"
        )
        print(f"Code processing result: {code_result['success']}")
        
        # Test agent chat
        print("\n🤖 Testing agent chat...")
        agent_result = langchain_service.chat_with_agent(
            "Can you help me analyze a simple Java class?"
        )
        print(f"Agent chat result: {agent_result['success']}")
        
        print("✅ LangchainService tests completed!")
        return True
        
    except Exception as e:
        print(f"❌ Memory tests failed: {str(e)}")
        return False

def test_ai_service_integration():
        return False

def test_knowledge_base_service():
    """Test KnowledgeBaseService với Langchain integration"""
    print("=" * 50)
    print("🧪 Testing KnowledgeBaseService with Langchain...")
    print("=" * 50)
    
    try:
        # Khởi tạo service
        kb_service = KnowledgeBaseService()
        
        # Test vector store initialization
        print("\n🗄️ Testing vector store initialization...")
        if kb_service.vector_store:
            print("✅ Vector store initialized successfully")
        else:
            print("❌ Vector store initialization failed")
            return False
        
        # Test retriever
        print("\n🔍 Testing retriever creation...")
        retriever = kb_service.get_vector_store_as_retriever()
        if retriever:
            print("✅ Retriever created successfully")
        else:
            print("❌ Retriever creation failed")
        
        # Test search (nếu có data)
        print("\n🔎 Testing search functionality...")
        search_result = kb_service.search_in_vector_db("Java programming", n_results=2)
        print(f"Search result: {search_result[0]} (found {len(search_result[1])} results)")
        
        print("✅ KnowledgeBaseService tests completed!")
        return True
        
    except Exception as e:
        print(f"❌ KnowledgeBaseService test failed: {str(e)}")
        return False

def test_memory_and_session_management():
    """Test memory và session management"""
    print("=" * 50)
    print("🧪 Testing Memory and Session Management...")
    print("=" * 50)
    
    try:
        # Khởi tạo service
        langchain_service = LangchainService()
        
        # Test 1: Basic session memory
        print("\n1️⃣ Testing basic session memory...")
        session_id = "test_session_123"
        
        # Chat với session
        result1 = langchain_service.chat_with_rag(
            question="What is Java programming?",
            session_id=session_id
        )
        print(f"First chat result: {result1['success']}")
        
        # Chat tiếp theo trong cùng session
        result2 = langchain_service.chat_with_rag(
            question="Can you give me more details about what we just discussed?",
            session_id=session_id
        )
        print(f"Second chat result: {result2['success']}")
        
        # Test 2: Search history
        print("\n2️⃣ Testing search history...")
        search_history = langchain_service.get_session_search_history(session_id)
        print(f"Search history entries: {len(search_history)}")
        
        for i, entry in enumerate(search_history):
            print(f"  Entry {i+1}: {entry['question'][:50]}...")
        
        # Test 3: Memory stats
        print("\n3️⃣ Testing memory statistics...")
        memory_stats = langchain_service.get_memory_stats()
        print(f"Total sessions: {memory_stats['total_sessions']}")
        print(f"Total search entries: {memory_stats['total_search_history_entries']}")
        
        # Test 4: Clear session memory
        print("\n4️⃣ Testing clear session memory...")
        langchain_service.clear_session_memory(session_id)
        
        # Verify cleared
        search_history_after = langchain_service.get_session_search_history(session_id)
        print(f"Search history after clear: {len(search_history_after)}")
        
        # Test 5: Related searches detection
        print("\n5️⃣ Testing related searches detection...")
        
        # Tạo một số searches tương tự
        similar_questions = [
            "What is Java programming language?",
            "Explain Java programming",
            "Tell me about Java programming concepts"
        ]
        
        for question in similar_questions:
            langchain_service.chat_with_rag(question, session_id="similarity_test")
        
        # Test similarity detection
        result_with_context = langchain_service.chat_with_rag(
            "What is Java programming?", 
            session_id="similarity_test"
        )
        
        search_context = result_with_context.get("search_context", {})
        print(f"Cache hit: {search_context.get('cache_hit', False)}")
        print(f"Related searches found: {len(search_context.get('related_searches', []))}")
        
        print("✅ Memory and session management tests completed!")
        return True
        
    except Exception as e:
def test_ai_service_integration():
    """Test AIService với Langchain integration"""
    print("=" * 50)
    print("🧪 Testing AIService with Langchain integration...")
    print("=" * 50)
    
    try:
        # Khởi tạo services
        langchain_service = LangchainService()
        ai_service = AIService(langchain_service=langchain_service)
        
        # Test normal chat với session
        print("\n💬 Testing normal chat with session...")
        session_id = "test_ai_session"
        
        chat_result = ai_service.chat_with_ai(
            "Explain the concept of inheritance in Java programming",
            history=[],
            is_quick_action=False,
            session_id=session_id
        )
        print(f"Chat result: {chat_result['success']}")
        if chat_result['success']:
            print(f"Response preview: {chat_result['response'][:100]}...")
            print(f"Source: {chat_result.get('tokens_info', {}).get('source', 'unknown')}")
            print(f"Session ID: {chat_result.get('session_id')}")
        
        # Test quick action
        print("\n⚡ Testing quick action...")
        quick_result = ai_service.chat_with_ai(
            "Add comments to this Java code: public class Test { public void run() { System.out.println(\"test\"); } }",
            history=[],
            is_quick_action=True
        )
        print(f"Quick action result: {quick_result['success']}")
        if quick_result['success']:
            print(f"Response preview: {quick_result['response'][:100]}...")
        
        print("✅ AIService integration tests completed!")
        return True
        
    except Exception as e:
        print(f"❌ AIService integration test failed: {str(e)}")
        return False
    """Test AIService với Langchain integration"""
    print("=" * 50)
    print("🧪 Testing AIService with Langchain integration...")
    print("=" * 50)
    
    try:
        # Khởi tạo services
        langchain_service = LangchainService()
        ai_service = AIService(langchain_service=langchain_service)
        
        # Test normal chat
        print("\n💬 Testing normal chat...")
        chat_result = ai_service.chat_with_ai(
            "Explain the concept of inheritance in Java programming",
            history=[],
            is_quick_action=False
        )
        print(f"Chat result: {chat_result['success']}")
        if chat_result['success']:
            print(f"Response preview: {chat_result['response'][:100]}...")
            print(f"Source: {chat_result.get('tokens_info', {}).get('source', 'unknown')}")
        
        # Test quick action
        print("\n⚡ Testing quick action...")
        quick_result = ai_service.chat_with_ai(
            "Add comments to this Java code: public class Test { public void run() { System.out.println(\"test\"); } }",
            history=[],
            is_quick_action=True
        )
        print(f"Quick action result: {quick_result['success']}")
        if quick_result['success']:
            print(f"Response preview: {quick_result['response'][:100]}...")
        
        print("✅ AIService integration tests completed!")
        return True
        
    except Exception as e:
        print(f"❌ AIService integration test failed: {str(e)}")
        return False

def test_full_integration():
    """Test full integration với tất cả components"""
    print("=" * 50)
    print("🧪 Testing Full Langchain Integration...")
    print("=" * 50)
    
    try:
        # Test từng component
        tests = [
            ("LangchainService", test_langchain_service),
            ("KnowledgeBaseService", test_knowledge_base_service), 
            ("Memory & Session Management", test_memory_and_session_management),
            ("AIService Integration", test_ai_service_integration)
        ]
        
        results = {}
        for test_name, test_func in tests:
            print(f"\n🔄 Running {test_name} test...")
            results[test_name] = test_func()
        
        # Summary
        print("\n" + "=" * 50)
        print("📊 TEST SUMMARY")
        print("=" * 50)
        
        total_tests = len(results)
        passed_tests = sum(results.values())
        
        for test_name, passed in results.items():
            status = "✅ PASSED" if passed else "❌ FAILED"
            print(f"{test_name}: {status}")
        
        print(f"\nOverall: {passed_tests}/{total_tests} tests passed")
        
        if passed_tests == total_tests:
            print("🎉 All Langchain integration tests PASSED!")
            print("\n📝 Next steps:")
            print("1. Install packages: pip install -r requirements.txt")
            print("2. Start the server: python app.py")
            print("3. Test API endpoints via Swagger UI")
            return True
        else:
            print("⚠️ Some tests failed. Please check the error messages above.")
            return False
            
    except Exception as e:
        print(f"❌ Full integration test failed: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 Starting Langchain Integration Tests...")
    print("This will test all Langchain components and integrations.\n")
    
    try:
        success = test_full_integration()
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print("\n\n⏹️ Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n💥 Unexpected error: {str(e)}")
        sys.exit(1)
