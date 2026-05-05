import asyncio
from elasticsearch import AsyncElasticsearch
from app.conf.app_config import ESConfig,app_config

class ESClientManager:

    def __init__(self,config:ESConfig):
        self.client:AsyncElasticsearch | None = None
        self.config : ESConfig = config

    def get_url(self):
        return f"http://{self.config.host}:{self.config.port}"

    def init(self):
        self.client = AsyncElasticsearch(hosts = [self.get_url()])   # 不需要api_key是因为我们在docker-compose.yaml文件中关于ES的部分加上了不需要验证的字段

    async def close(self):
        await self.client.close()

es_client_manager = ESClientManager(app_config.es)

if __name__ == "__main__":

    es_client_manager.init()
    client = es_client_manager.client

    async def test():
        # 创建索引
        await client.indices.create(
            index="bookss",
        )

        # 写入数据，这里index作为动词，表示写入的意思
        await client.index(
            index="bookss",
            document={
                "name": "Snow Crash",
                "author": "Neal Stephenson",
                "release_date": "1992-06-01",
                "page_count": 470
            },
        )

        # 查询索引下面的所有文档信息
        resp = await client.search(
            index="bookss",
        )
        print(resp)

        await es_client_manager.close()

    asyncio.run(test())

