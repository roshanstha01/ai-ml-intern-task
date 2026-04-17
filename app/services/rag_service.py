from typing import List, Dict

from app.services.embedding_service import EmbeddingService
from app.services.llm_service import OllamaService
from app.services.vector_store import QdrantVectorStore


class RAGService:
    def __init__(self) -> None:
        self.embedding_service = EmbeddingService()
        self.vector_store = QdrantVectorStore()
        self.llm_service = OllamaService()

    def retrieve_context(self, query: str, limit: int = 5) -> List[str]:
        query_embedding = self.embedding_service.embed_query(query)
        search_results = self.vector_store.search(query_embedding=query_embedding, limit=limit)

        contexts = []
        for result in search_results:
            payload = result.payload
            if payload and "chunk_text" in payload:
                contexts.append(payload["chunk_text"])

        return contexts

    def build_messages(
        self,
        query: str,
        context_chunks: List[str],
        history: List[Dict[str, str]],
    ) -> List[Dict[str, str]]:
        context_text = "\n\n".join(context_chunks) if context_chunks else "No relevant context found."

        system_prompt = (
            "You are a helpful AI assistant.\n"
            "Use ONLY the provided context to answer.\n"
            "If the answer is not in the context, say: 'I could not find this in the document.'\n"
            "Keep answers short and clear."
        )

        messages: List[Dict[str, str]] = [
            {"role": "system", "content": system_prompt},
            {
                "role": "system",
                "content": f"Context:\n{context_text}"
            },
        ]

        recent_history = history[-6:] if len(history) > 6 else history
        messages.extend(recent_history)
        messages.append({"role": "user", "content": query})

        return messages

    def answer_query(self, query: str, history: List[Dict[str, str]]) -> str:
        context_chunks = self.retrieve_context(query=query, limit=5)
        messages = self.build_messages(query=query, context_chunks=context_chunks, history=history)
        return self.llm_service.generate_response(messages)