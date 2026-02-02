"""
Performance testing script for RAG pipeline
Run: python test_performance.py
"""

import time
from rag_pipeline import RAGPipeline
import os

def test_performance():
    print("🧪 RAG Pipeline Performance Test\n")
    print("=" * 50)
    
    # Test 1: Initialization
    print("\n1️⃣ Testing initialization...")
    start = time.time()
    rag = RAGPipeline()
    init_time = time.time() - start
    print(f"   ⏱️  Initialization: {init_time:.2f}s")
    
    # Test 2: Document loading
    print("\n2️⃣ Testing document loading...")
    test_file = "test.txt"
    
    # Create test file if not exists
    if not os.path.exists(test_file):
        with open(test_file, 'w') as f:
            f.write("""
            Artificial Intelligence (AI) is transforming healthcare.
            Machine learning algorithms can now detect diseases earlier.
            AI systems analyze medical images with high accuracy.
            Natural language processing helps doctors understand patient records.
            The future of medicine will be powered by AI technology.
            """ * 20)  # Repeat to make substantial doc
    
    start = time.time()
    docs = rag.load_documents(test_file)
    load_time = time.time() - start
    print(f"   ⏱️  Document loading: {load_time:.2f}s")
    print(f"   📄 Chunks created: {len(docs)}")
    
    # Test 3: Vectorstore creation
    print("\n3️⃣ Testing vectorstore creation...")
    start = time.time()
    rag.create_vectorstore(docs)
    vector_time = time.time() - start
    print(f"   ⏱️  Vectorstore creation: {vector_time:.2f}s")
    
    # Test 4: QA chain setup
    print("\n4️⃣ Testing QA chain setup...")
    start = time.time()
    rag.setup_qa_chain()
    chain_time = time.time() - start
    print(f"   ⏱️  QA chain setup: {chain_time:.2f}s")
    
    # Test 5: First query (cold)
    print("\n5️⃣ Testing first query (cold)...")
    question = "What is this document about?"
    start = time.time()
    answer, sources = rag.query(question)
    first_query_time = time.time() - start
    print(f"   ⏱️  First query: {first_query_time:.2f}s")
    print(f"   📝 Answer length: {len(answer)} chars")
    print(f"   📚 Sources: {len(sources)}")
    
    # Test 6: Repeated query (should be cached)
    print("\n6️⃣ Testing repeated query (cached)...")
    start = time.time()
    answer2, sources2 = rag.query(question)
    cached_query_time = time.time() - start
    print(f"   ⏱️  Cached query: {cached_query_time:.2f}s")
    print(f"   🚀 Speedup: {first_query_time/cached_query_time:.1f}x faster!")
    
    # Test 7: Different query
    print("\n7️⃣ Testing different query...")
    question2 = "What are the main points?"
    start = time.time()
    answer3, sources3 = rag.query(question2)
    second_query_time = time.time() - start
    print(f"   ⏱️  New query: {second_query_time:.2f}s")
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 PERFORMANCE SUMMARY")
    print("=" * 50)
    
    total_time = init_time + load_time + vector_time + chain_time
    
    print(f"\n⏱️  Total Setup Time: {total_time:.2f}s")
    print(f"   └─ Initialization: {init_time:.2f}s ({init_time/total_time*100:.1f}%)")
    print(f"   └─ Document load: {load_time:.2f}s ({load_time/total_time*100:.1f}%)")
    print(f"   └─ Vectorstore: {vector_time:.2f}s ({vector_time/total_time*100:.1f}%)")
    print(f"   └─ QA chain: {chain_time:.2f}s ({chain_time/total_time*100:.1f}%)")
    
    print(f"\n⏱️  Query Performance:")
    print(f"   └─ First query: {first_query_time:.2f}s")
    print(f"   └─ Cached query: {cached_query_time:.2f}s")
    print(f"   └─ New query: {second_query_time:.2f}s")
    
    print(f"\n🎯 Performance Rating:")
    if total_time < 5:
        print("   ⭐⭐⭐⭐⭐ EXCELLENT - Very fast!")
    elif total_time < 10:
        print("   ⭐⭐⭐⭐ GOOD - Fast enough")
    elif total_time < 15:
        print("   ⭐⭐⭐ OKAY - Could be faster")
    else:
        print("   ⭐⭐ SLOW - Needs optimization")
    
    # Recommendations
    print(f"\n💡 Recommendations:")
    if init_time > 5:
        print("   ⚠️  Slow initialization - embeddings taking too long")
        print("      → Use @st.cache_resource in Streamlit")
    if vector_time > 5:
        print("   ⚠️  Slow vectorstore - too many chunks")
        print("      → Increase chunk_size or reduce document size")
    if first_query_time > 8:
        print("   ⚠️  Slow queries - Ollama might be cold")
        print("      → Run: ollama run rag-assistant '' (to warm up)")
    if cached_query_time > 0.5:
        print("   ⚠️  Cache not working properly")
        print("      → Check @lru_cache is enabled")
    
    if total_time < 10 and first_query_time < 5:
        print("   ✅ Everything looks great!")
    
    print("\n" + "=" * 50)
    
    # Cleanup
    rag.reset()
    print("\n✅ Test complete!")

if __name__ == "__main__":
    try:
        test_performance()
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        print("\n💡 Make sure:")
        print("   1. Ollama is running: ollama serve")
        print("   2. Model exists: ollama list | grep rag-assistant")
        print("   3. Dependencies installed: pip install -r requirements.txt")