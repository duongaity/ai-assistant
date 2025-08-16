#!/usr/bin/env python3
"""
Demo script để showcase Langchain Memory functionality

Script này demonstrate:
- Session-based memory management
- Search history persistence
- Related searches detection
- Conversation continuity
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import time
import json
from services.langchain_service import LangchainService
from services.ai_service import AIService

def demo_session_memory():
    """Demo session-based memory functionality"""
    print("🎭 " + "=" * 60)
    print("DEMO: Session-based Memory Management")
    print("=" * 60)
    
    # Khởi tạo services
    langchain_service = LangchainService()
    ai_service = AIService(langchain_service=langchain_service)
    
    # Scenario 1: Conversation with memory
    print("\n🗣️ Scenario 1: Conversation with Memory")
    print("-" * 40)
    
    session_id = "demo_session_001"
    
    conversations = [
        "What is Java programming language?",
        "What are the main features we just discussed?",
        "Can you explain inheritance in more detail?",
        "How does it relate to what we talked about earlier?"
    ]
    
    for i, question in enumerate(conversations, 1):
        print(f"\n👤 User: {question}")
        
        result = ai_service.chat_with_ai(
            message=question,
            session_id=session_id,
            is_quick_action=False
        )
        
        if result["success"]:
            response = result["response"][:200] + "..." if len(result["response"]) > 200 else result["response"]
            print(f"🤖 Assistant: {response}")
            
            # Show context info
            search_context = result.get("search_context", {})
            if search_context.get("cache_hit"):
                print(f"💾 Cache hit! Found {len(search_context.get('related_searches', []))} related searches")
        else:
            print(f"❌ Error: {result.get('error')}")
        
        time.sleep(1)  # Pause for readability
    
    return session_id

def demo_search_history():
    """Demo search history functionality"""
    print("\n📚 " + "=" * 60)
    print("DEMO: Search History Management")
    print("=" * 60)
    
    langchain_service = LangchainService()
    
    # Get search history from previous demo
    session_id = "demo_session_001"
    search_history = langchain_service.get_session_search_history(session_id, limit=10)
    
    print(f"\n📊 Search History for Session: {session_id}")
    print("-" * 40)
    
    for i, entry in enumerate(search_history, 1):
        print(f"\n{i}. 📝 Question: {entry['question']}")
        print(f"   ⏰ Time: {entry['timestamp']}")
        print(f"   📄 Sources: {entry['source_docs_count']} documents")
        print(f"   💬 Answer Preview: {entry['answer'][:100]}...")

def demo_similar_questions():
    """Demo related questions detection"""
    print("\n🔍 " + "=" * 60)
    print("DEMO: Related Questions Detection")
    print("=" * 60)
    
    langchain_service = LangchainService()
    session_id = "similarity_demo"
    
    # Create similar questions
    similar_questions = [
        "What is Python programming?",
        "Explain Python programming language",
        "Tell me about Python development",
        "Python programming concepts"
    ]
    
    print("\n🎯 Creating similar questions...")
    for question in similar_questions:
        print(f"  ➤ {question}")
        langchain_service.chat_with_rag(question, session_id=session_id)
        time.sleep(0.5)
    
    # Now ask a similar question
    print(f"\n🔄 Testing similarity detection...")
    test_question = "What is Python programming language?"
    print(f"👤 User: {test_question}")
    
    result = langchain_service.chat_with_rag(test_question, session_id=session_id)
    
    if result["success"]:
        search_context = result.get("search_context", {})
        
        print(f"\n📈 Similarity Analysis:")
        print(f"  💾 Cache Hit: {search_context.get('cache_hit', False)}")
        print(f"  🔗 Related Searches: {len(search_context.get('related_searches', []))}")
        
        for i, related in enumerate(search_context.get('related_searches', []), 1):
            print(f"    {i}. \"{related['question']}\" (similarity: {related['similarity']:.2f})")

def demo_memory_statistics():
    """Demo memory statistics"""
    print("\n📊 " + "=" * 60)
    print("DEMO: Memory Statistics")
    print("=" * 60)
    
    langchain_service = LangchainService()
    
    # Get memory stats
    stats = langchain_service.get_memory_stats()
    
    print(f"\n🏢 Overall Statistics:")
    print(f"  📱 Total Sessions: {stats['total_sessions']}")
    print(f"  📝 Total Search Entries: {stats['total_search_history_entries']}")
    
    print(f"\n📋 Session Details:")
    for session_id, session_stats in stats['sessions'].items():
        print(f"  🆔 Session: {session_id}")
        print(f"    💬 Conversation Messages: {session_stats['conversation_messages']}")
        print(f"    🔍 Search History Entries: {session_stats['search_history_entries']}")

def demo_memory_cleanup():
    """Demo memory cleanup"""
    print("\n🧹 " + "=" * 60)
    print("DEMO: Memory Cleanup")
    print("=" * 60)
    
    langchain_service = LangchainService()
    
    # Show stats before cleanup
    stats_before = langchain_service.get_memory_stats()
    print(f"\n📊 Before Cleanup:")
    print(f"  Sessions: {stats_before['total_sessions']}")
    print(f"  Search Entries: {stats_before['total_search_history_entries']}")
    
    # Clean up demo sessions
    demo_sessions = ["demo_session_001", "similarity_demo"]
    
    for session_id in demo_sessions:
        print(f"\n🗑️ Clearing session: {session_id}")
        langchain_service.clear_session_memory(session_id)
    
    # Show stats after cleanup
    stats_after = langchain_service.get_memory_stats()
    print(f"\n📊 After Cleanup:")
    print(f"  Sessions: {stats_after['total_sessions']}")
    print(f"  Search Entries: {stats_after['total_search_history_entries']}")

def main():
    """Main demo function"""
    print("🚀 " + "=" * 60)
    print("LANGCHAIN MEMORY FUNCTIONALITY DEMO")
    print("=" * 60)
    print("\nThis demo showcases advanced memory features:")
    print("• Session-based conversation memory")
    print("• Search history persistence")
    print("• Related questions detection")
    print("• Memory statistics and cleanup")
    print("\n" + "=" * 60)
    
    try:
        # Run all demos
        input("\n👆 Press Enter to start Session Memory demo...")
        session_id = demo_session_memory()
        
        input("\n👆 Press Enter to show Search History...")
        demo_search_history()
        
        input("\n👆 Press Enter to demo Similar Questions...")
        demo_similar_questions()
        
        input("\n👆 Press Enter to show Memory Statistics...")
        demo_memory_statistics()
        
        input("\n👆 Press Enter to demo Memory Cleanup...")
        demo_memory_cleanup()
        
        print("\n🎉 " + "=" * 60)
        print("DEMO COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        print("\n✨ Key Features Demonstrated:")
        print("• ✅ Session-based memory maintains conversation context")
        print("• ✅ Search history prevents duplicate processing")
        print("• ✅ Related questions detection improves efficiency")
        print("• ✅ Memory statistics provide insights")
        print("• ✅ Cleanup functionality manages memory usage")
        
        print(f"\n📝 Next Steps:")
        print("1. 🚀 Start the backend server: python app.py")
        print("2. 🌐 Test via API endpoints with session_id parameter")
        print("3. 📱 Frontend can now maintain user sessions")
        print("4. 📊 Monitor memory usage via /knowledge-base/memory/sessions")
        
    except KeyboardInterrupt:
        print("\n\n⏹️ Demo interrupted by user")
    except Exception as e:
        print(f"\n💥 Demo error: {str(e)}")

if __name__ == "__main__":
    main()
