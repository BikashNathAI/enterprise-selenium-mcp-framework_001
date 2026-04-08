"""
RAG Knowledge Base
Stores your test artifacts — page objects, locators,
existing tests — so AI generates relevant test cases
that match YOUR actual application.
"""
import json
import os
from pathlib import Path
from loguru import logger


class TestKnowledgeBase:
    """
    Builds a knowledge base from your framework files.
    AI uses this to generate smarter, relevant tests.

    Works in two modes:
    1. Simple mode  — JSON-based (no extra libraries)
    2. Vector mode  — ChromaDB (semantic search)
    """

    def __init__(self, use_vector: bool = False):
        self.use_vector  = use_vector
        self.knowledge   = []
        self.base_dir    = Path(__file__).resolve().parent.parent.parent
        self.db_path     = self.base_dir / "mcp_agent" / "rag" / "knowledge_db"

        if use_vector:
            self._init_vector_db()
        else:
            logger.info("KnowledgeBase: using simple JSON mode")

    def _init_vector_db(self):
        """Initialize ChromaDB for semantic search."""
        try:
            import chromadb
            self.chroma_client = chromadb.PersistentClient(
                path=str(self.db_path)
            )
            self.collection = self.chroma_client.get_or_create_collection(
                name="test_knowledge"
            )
            logger.info("KnowledgeBase: ChromaDB vector mode ready")
        except ImportError:
            logger.warning("ChromaDB not available — using simple mode")
            self.use_vector = False

    def build_from_framework(self):
        """
        Scan your framework and build knowledge base
        from existing tests, page objects, and features.
        """
        logger.info("Building knowledge base from framework...")

        # Scan page objects
        pages_dir = self.base_dir / "pages"
        for f in pages_dir.glob("*.py"):
            if f.name != "__init__.py":
                content = f.read_text(encoding="utf-8", errors="ignore")
                self._add_knowledge(
                    doc_id   = f"page_{f.stem}",
                    content  = content,
                    metadata = {
                        "type":     "page_object",
                        "filename": f.name,
                        "module":   f.stem
                    }
                )
                logger.debug(f"Added page: {f.name}")

        # Scan existing tests
        tests_dir = self.base_dir / "tests"
        for f in tests_dir.rglob("test_*.py"):
            content = f.read_text(encoding="utf-8", errors="ignore")
            self._add_knowledge(
                doc_id   = f"test_{f.stem}",
                content  = content,
                metadata = {
                    "type":     "existing_test",
                    "filename": f.name,
                    "module":   f.stem
                }
            )
            logger.debug(f"Added test: {f.name}")

        # Scan feature files
        features_dir = self.base_dir / "features"
        for f in features_dir.glob("*.feature"):
            content = f.read_text(encoding="utf-8", errors="ignore")
            self._add_knowledge(
                doc_id   = f"feature_{f.stem}",
                content  = content,
                metadata = {
                    "type":     "gherkin_feature",
                    "filename": f.name,
                    "module":   f.stem
                }
            )
            logger.debug(f"Added feature: {f.name}")

        # Scan step definitions
        steps_dir = self.base_dir / "steps"
        for f in steps_dir.glob("*.py"):
            if f.name != "__init__.py":
                content = f.read_text(encoding="utf-8", errors="ignore")
                self._add_knowledge(
                    doc_id   = f"step_{f.stem}",
                    content  = content,
                    metadata = {
                        "type":     "step_definitions",
                        "filename": f.name,
                        "module":   f.stem
                    }
                )

        total = len(self.knowledge)
        logger.success(f"Knowledge base built: {total} documents")
        return total

    def _add_knowledge(self, doc_id: str,
                       content: str, metadata: dict):
        """Add a document to the knowledge base."""
        entry = {
            "id":       doc_id,
            "content":  content[:2000],  # Trim large files
            "metadata": metadata
        }
        self.knowledge.append(entry)

        if self.use_vector and hasattr(self, "collection"):
            try:
                self.collection.upsert(
                    documents=[content[:2000]],
                    metadatas=[metadata],
                    ids=[doc_id]
                )
            except Exception as e:
                logger.warning(f"Vector add failed: {e}")

    def search(self, query: str, top_k: int = 3) -> list:
        """
        Search knowledge base for relevant context.
        Returns most relevant documents for the query.
        """
        if self.use_vector and hasattr(self, "collection"):
            return self._vector_search(query, top_k)
        return self._simple_search(query, top_k)

    def _simple_search(self, query: str, top_k: int) -> list:
        """Keyword-based search."""
        query_words = query.lower().split()
        scored      = []

        for doc in self.knowledge:
            content_lower = doc["content"].lower()
            score = sum(
                1 for word in query_words
                if word in content_lower
            )
            if score > 0:
                scored.append((score, doc))

        scored.sort(key=lambda x: x[0], reverse=True)
        results = [doc for _, doc in scored[:top_k]]
        logger.debug(f"Simple search '{query}': {len(results)} results")
        return results

    def _vector_search(self, query: str, top_k: int) -> list:
        """Semantic vector search with ChromaDB."""
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=min(top_k, self.collection.count())
            )
            docs = []
            for i, doc in enumerate(results["documents"][0]):
                docs.append({
                    "content":  doc,
                    "metadata": results["metadatas"][0][i]
                })
            return docs
        except Exception as e:
            logger.warning(f"Vector search failed: {e}")
            return self._simple_search(query, top_k)

    def get_context_for_ai(self, query: str) -> str:
        """
        Get formatted context string to inject into AI prompt.
        This makes AI generate tests relevant to YOUR framework.
        """
        results = self.search(query, top_k=3)
        if not results:
            return "No existing context found."

        context_parts = []
        for doc in results:
            doc_type = doc["metadata"].get("type", "unknown")
            filename = doc["metadata"].get("filename", "unknown")
            content  = doc["content"][:500]
            context_parts.append(
                f"[{doc_type}] {filename}:\n{content}"
            )

        return "\n\n".join(context_parts)

    def save(self, path: str = None):
        """Save knowledge base to JSON."""
        save_path = path or str(
            self.base_dir / "mcp_agent" / "rag" / "knowledge.json"
        )
        with open(save_path, "w") as f:
            json.dump(self.knowledge, f, indent=2)
        logger.info(f"Knowledge base saved: {save_path}")

    def load(self, path: str = None):
        """Load knowledge base from JSON."""
        load_path = path or str(
            self.base_dir / "mcp_agent" / "rag" / "knowledge.json"
        )
        if os.path.exists(load_path):
            with open(load_path) as f:
                self.knowledge = json.load(f)
            logger.info(f"Knowledge base loaded: {len(self.knowledge)} docs")
        else:
            logger.warning("No saved knowledge base found")