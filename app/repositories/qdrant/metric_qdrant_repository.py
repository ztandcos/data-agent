from qdrant_client import AsyncQdrantClient
from qdrant_client.models import VectorParams, Distance
from app.conf.app_config import app_config
from qdrant_client.models import PointStruct
from app.entities.metric_info import MetricInfo
class MetricQdrantRepository:
    collection_name = "metric_info_collectioin"
    def __init__(self,client:AsyncQdrantClient):
        self.client = client
    
    async def ensure_collection(self):
        if not await self.client.collection_exists(self.collection_name):
            await self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(size=app_config.qdrant.embedding_size, distance=Distance.COSINE),
            )

    async def upsert(self,ids:list[str],embedding:list[list[float]],payloads:list[dict],batch_size : int = 10):
        # 合成为一个pointstruct列表
        points : list[PointStruct] = [PointStruct(id = id,vector = embedding,payload = payloads) for id,embedding,payloads in 
                                      zip(ids,embedding,payloads)]
        # 批量处理写入
        # self.client.upsert(collection_name=self.collection_name,points=points)
        for i in range(0,len(points),batch_size):
            batch_points : list[PointStruct] = points[i:i+batch_size]
            await self.client.upsert(collection_name=self.collection_name,points=batch_points)

    async def search(self,embedding:list[float],score_threshold : float = 0.6,limit : int = 20)->list[MetricInfo]:
       
        result = await self.client.query_points(
            collection_name=self.collection_name,
            query=embedding,
            limit=limit,
            score_threshold=score_threshold
        )
        return [MetricInfo(**point.payload) for point in result.points]
