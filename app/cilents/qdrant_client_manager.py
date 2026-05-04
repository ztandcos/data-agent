import asyncio

from app.conf.app_config import QdrantConfig, app_config
from qdrant_client import AsyncQdrantClient
from qdrant_client.models import Distance, VectorParams
from qdrant_client.models import PointStruct

class QdrantClientManager:
    def __init__(self, config: QdrantConfig):
        self.client: AsyncQdrantClient | None = None
        self.config: QdrantConfig = config

    def _get_url(self):
        return f"http://{self.config.host}:{self.config.port}"

    def init(self):
        self.client = AsyncQdrantClient(url=self._get_url())

    async def close(self):
        if self.client is not None:
            await self.client.close()

qdrant_client_manager = QdrantClientManager(app_config.qdrant)

if __name__ == "__main__":
    qdrant_client_manager.init()
    client = qdrant_client_manager.client
    if client is None:
        raise RuntimeError("Qdrant client is not initialized")

    async def test():
        try:
            # 创建集合
            if not await client.collection_exists(collection_name="text_collection_async"):
                await client.create_collection(
                    collection_name="text_collection_async",
                    vectors_config=VectorParams(
                        size=4,
                        distance=Distance.COSINE,
                    ),
                )

            # 写入数据
            await client.upsert(
                collection_name="text_collection_async",
                points=[
                    PointStruct(id=1, vector=[0.05, 0.61, 0.76, 0.74], payload={"city": "BerLin"}),
                    PointStruct(id=2, vector=[0.19, 0.61, 0.76, 0.74], payload={"city": "London"}),
                    PointStruct(id=3, vector=[0.36, 0.61, 0.76, 0.74], payload={"city": "Moscow"}),
                    PointStruct(id=4, vector=[0.18, 0.61, 0.76, 0.74], payload={"city": "Beijing"}),
                    PointStruct(id=5, vector=[0.35, 0.61, 0.76, 0.74], payload={"city": "Mumbei"}),
                ],
            )

            # 查询数据
            # search_results = (await client.query_points(
            #     collection_name="text_collection",
            #     query=[0.2, 0.1, 0.9, 0.7],
            #     limit=3,
            # )).points

            # 或者
            search_results = await client.query_points(
                collection_name="text_collection_async",
                query=[0.2, 0.1, 0.9, 0.7],
                limit=3,
            )
            print(search_results.points)
        finally:
            await qdrant_client_manager.close()
    
    asyncio.run(test())