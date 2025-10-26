from typing import List, Dict, Any
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer

import re
from src.rag.scorecard import ReadinessScorecard


class RAGPipeline:
    """
    Retrieval-Augmented Generation (RAG) pipeline for regulatory document search and explanation.
    Handles embedding, chunking, retrieval, and explanation generation.
    """

    def __init__(
        self,
        db_client=None,
        chroma_host="chroma",
        chroma_port=8000,
        collection_name="regulations",
    ):
        """
        Initialize the RAGPipeline.
        Args:
                db_client: MongoDB client or similar for document storage
                chroma_host: Hostname for ChromaDB (default: 'chroma' for Docker Compose)
                chroma_port: Port for ChromaDB (default: 8000)
                collection_name: Name of the ChromaDB collection
        """
        self.db_client = db_client
        self.chroma_client = chromadb.HttpClient(
            host=chroma_host, port=chroma_port, settings=Settings(allow_reset=True)
        )
        self.collection = self.chroma_client.get_or_create_collection(collection_name)
        # Load a local embedding model (MiniLM is small and fast)
        self.embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
        self.scorecard = ReadinessScorecard()  # Initialize ReadinessScorecard

    def chunk_and_ingest_markdown(
        self, markdown_text: str, source_file: str, is_test: bool = False
    ) -> int:
        """
        Split a regulatory markdown document into chunks (by article/section), embed, and upsert to ChromaDB.
        Each chunk is stored with metadata for explainable retrieval.
        Returns:
                int: Number of chunks ingested.
        """
        chunks = []
        # Simple regex: split by 'Article X.Y.Z' or 'SECTION X' or numbered headings
        article_pattern = re.compile(
            r"(Article\s+\d+(?:\.\d+)*:?.*?)(?=\n[A-Z]|\nArticle|\nSECTION|\n\d+\.|\Z)",
            re.DOTALL,
        )
        section_pattern = re.compile(
            r"(SECTION\s+\d+:?.*?)(?=\n[A-Z]|\nArticle|\nSECTION|\n\d+\.|\Z)", re.DOTALL
        )
        # Try to find articles first
        articles = article_pattern.findall(markdown_text)
        if not articles:
            # Fallback: try sections
            articles = section_pattern.findall(markdown_text)
        if not articles:
            # Fallback: split by paragraphs
            articles = [p for p in markdown_text.split("\n\n") if p.strip()]
        for i, chunk in enumerate(articles):
            chunk_id = f"{'test_' if is_test else ''}{source_file}_chunk_{i+1}"
            metadata = {"source_file": source_file, "chunk_index": i + 1}
            embedding = self.embed_text(chunk)
            self.collection.upsert(
                ids=[chunk_id],
                embeddings=[embedding],
                documents=[chunk],
                metadatas=[metadata],
            )
        return len(articles)

    def embed_text(self, text: str) -> List[float]:
        """
        Embed text into a vector using sentence-transformers.
        Args:
                text (str): Text to embed.
        Returns:
                List[float]: Embedding vector.
        """
        return self.embedding_model.encode(text).tolist()

    def upsert_document(self, doc_id: str, text: str, metadata: dict = None) -> None:
        """
        Upsert a document and its embedding into ChromaDB.
        Args:
                doc_id (str): Document ID.
                text (str): Document text.
                metadata (dict, optional): Metadata for the document.
        """
        embedding = self.embed_text(text)
        self.collection.upsert(
            ids=[doc_id],
            embeddings=[embedding],
            documents=[text],
            metadatas=[metadata or {}],
        )

    def retrieve(self, query: str, top_k: int = 2) -> List[Dict[str, Any]]:
        """
        Retrieve top_k relevant documents from ChromaDB.
        Args:
                query (str): Query string.
                top_k (int): Number of top results to return.
        Returns:
                List[Dict[str, Any]]: List of retrieved documents with metadata.
        """
        query_embedding = self.embed_text(query)
        results = self.collection.query(
            query_embeddings=[query_embedding], n_results=top_k
        )
        # Format results for downstream use
        docs = []
        for i in range(len(results["ids"][0])):
            docs.append(
                {
                    "id": results["ids"][0][i],
                    "text": results["documents"][0][i],
                    "metadata": results["metadatas"][0][i],
                    "distance": (
                        results["distances"][0][i] if "distances" in results else None
                    ),
                }
            )
        return docs

    def generate(self, query: str, retrieved_docs: List[Dict[str, Any]]) -> str:
        """
        Generate a response/explanation based on retrieved docs.
        Args:
                query (str): User query.
                retrieved_docs (List[Dict[str, Any]]): Retrieved documents.
        Returns:
                str: Generated explanation.
        """
        # TODO: Implement generation logic (LLM or template)
        if not retrieved_docs:
            return "No relevant regulations found."
        response = f"Query: '{query}'\nRelevant Regulations:\n"
        for doc in retrieved_docs:
            response += f"- {doc['text']}\n"
        return response

    def run(self, query: str) -> Dict[str, Any]:
        """
        Full RAG pipeline: embed, retrieve, generate.
        Args:
                query (str): User query.
        Returns:
                Dict[str, Any]: Pipeline output.
        """
        retrieved = self.retrieve(query)
        explanation = self.generate(query, retrieved)
        return {"query": query, "explanation": explanation, "regulations": retrieved}

    def run(
        self, query: str, top_k: int = 5, with_scorecard: bool = False
    ) -> Dict[str, Any]:
        """
        Run the RAG pipeline: retrieve relevant docs, generate answer, and explain mapping.
        If with_scorecard=True, also return readiness scorecard.
        Args:
                query (str): User query.
                top_k (int): Number of top results to return.
                with_scorecard (bool): Whether to include readiness scorecard.
        Returns:
                Dict[str, Any]: Pipeline output (with optional scorecard).
        """
        retrieved = self.retrieve(query)
        explanation = self.generate(query, retrieved)
        result = {"query": query, "explanation": explanation, "regulations": retrieved}
        if with_scorecard:
            # Assume explanations contain 'area', 'compliance', 'explanation' for each area
            scorecard = self.scorecard.score(
                explanation
            )  # Assuming score method exists
            result["scorecard"] = scorecard
        return result
