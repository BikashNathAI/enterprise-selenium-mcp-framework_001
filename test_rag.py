from mcp_agent.rag_engine import RAGEngine

r = RAGEngine()

print("\n" + "="*50)
print("TEST 1: Smart Search")
print("="*50)
results = r.search_similar("API user endpoint test")
for t in results:
    print(f"[{t['test_id']}] {t['title']} - similarity: {t['similarity']}")

print("\n" + "="*50)
print("TEST 2: NLP to Gherkin")
print("="*50)
g = r.nlp_to_gherkin("search product by category and filter by price")
print(g)

print("\n" + "="*50)
print("TEST 3: RAG Stats")
print("="*50)
print(r.get_stats())