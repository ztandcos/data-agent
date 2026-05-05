import asyncio
from typing import Any

import httpx
from langchain_core.embeddings import Embeddings

from app.conf.app_config import EmbeddingConfig, app_config


class TextEmbeddingsInferenceEmbeddings(Embeddings):
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")

    def _embed_url(self) -> str:
        return f"{self.base_url}/embed"

    @staticmethod
    def _normalize_response(data: Any) -> list[list[float]]:
        if isinstance(data, dict):
            data = data.get("embeddings") or data.get("data")

        if not isinstance(data, list):
            raise ValueError(f"Unexpected embedding response: {data!r}")

        if data and isinstance(data[0], dict):
            data = [item.get("embedding") for item in data]

        if data and isinstance(data[0], (int, float)):
            return [data]

        return data

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        with httpx.Client(timeout=60) as client:
            response = client.post(self._embed_url(), json={"inputs": texts})
            response.raise_for_status()
            return self._normalize_response(response.json())

    async def aembed_documents(self, texts: list[str]) -> list[list[float]]:
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(self._embed_url(), json={"inputs": texts})
            response.raise_for_status()
            return self._normalize_response(response.json())

    def embed_query(self, text: str) -> list[float]:
        return self.embed_documents([text])[0]

    async def aembed_query(self, text: str) -> list[float]:
        return (await self.aembed_documents([text]))[0]


class EmbeddingClientManager:
    def __init__(self, config: EmbeddingConfig):
        self.client: TextEmbeddingsInferenceEmbeddings | None = None
        self.config = config

    def _get_url(self):
        return f"http://{self.config.host}:{self.config.port}"

    def init(self):
        self.client = TextEmbeddingsInferenceEmbeddings(base_url=self._get_url())

embedding_client_manager = EmbeddingClientManager(app_config.embedding)

if __name__ == "__main__":
    embedding_client_manager.init()
    client = embedding_client_manager.client
    if client is None:
        raise RuntimeError("Embedding client is not initialized")

    async def test():
        text = "What is deep learning?"
        query_result = await client.aembed_query(text)  # 在原本的函数前面加上一个a就表示异步的方法
        print(query_result[:3])

    asyncio.run(test())
