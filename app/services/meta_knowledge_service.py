from app.clients.embedding_client_manager import TextEmbeddingsInferenceEmbeddings
from pathlib import Path
from omegaconf import OmegaConf
from app.conf.meta_config import MetaConfig
from app.repositories.mysql.meta.meta_mysql_repository import MetaMySQLRespository
from app.repositories.mysql.dw.dw_mysql_repository import DWMySQLRepository
from app.entities.table_info import TableInfo
from app.entities.column_info import ColumnInfo
from app.repositories.qdrant.column_qdrant_repository import ColumnQdrantRepository
import uuid
from app.entities.value_info import ValueInfo
from app.repositories.es.value_es_repository import ValueESRepository
from dataclasses import asdict


class MetaKnowledgeService:
    def __init__(self,meta_mysql_repository:MetaMySQLRespository,
                 dw_mysql_repository:DWMySQLRepository,
                 column_qdrant_repository:ColumnQdrantRepository,
                 embedding_client:TextEmbeddingsInferenceEmbeddings,
                 value_es_repository:ValueESRepository):
        self.meta_mysql_repository : MetaMySQLRespository = meta_mysql_repository
        self.dw_mysql_repository : DWMySQLRepository = dw_mysql_repository
        self.column_qdrant_repository : ColumnQdrantRepository = column_qdrant_repository
        self.embedding_client:TextEmbeddingsInferenceEmbeddings = embedding_client
        self.value_es_repository : ValueESRepository = value_es_repository
    async def build(self, config_path:Path):
       
        # 1.读取配置文件
        context = OmegaConf.load(config_path)
        schema = OmegaConf.structured(MetaConfig)
        meta_config : MetaConfig = OmegaConf.to_object(OmegaConf.merge(schema, context))
        # 打印指标配置测试
        # print(meta_config.metrics)
        # 2.根据配置文件同步指定的表信息
        if meta_config.tables:

            table_infos: list[TableInfo] = [] # 使用自己定义的业务类来代替底层的SQL类
            column_infos : list[ColumnInfo] = []
            # 2.1 将表信息和字段信息保存meta数据库中
            for table in meta_config.tables:
                # table -> table_info 
                table_info = TableInfo(id = table.name,
                                            name = table.name,
                                            description = table.description,
                                            role = table.role)
                table_infos.append(table_info)

                # 查询字段类型
                column_types = await self.dw_mysql_repository.get_column_types(table.name)
                
                for column in table.columns:
                    # 查询字段示例值
                    column_values = await self.dw_mysql_repository.get_column_values(table.name,column.name)
                    column_info = ColumnInfo(id = f"{table.name}.{column.name}",
                                                  name = column.name,
                                                  type = column_types[column.name],
                                                  role = column.role,
                                                  examples = column_values,
                                                  description = column.description,
                                                  alias = column.alias,
                                                  table_id = table.name)
                    column_infos.append(column_info)
            async with self.meta_mysql_repository.session.begin():
                """写入操作失误会回滚,成功会自动提交commit"""
                self.meta_mysql_repository.save_table_infos(table_infos)
                self.meta_mysql_repository.save_column_infos(column_infos)

            # 2.2 对字段信息建立向量索引
            await self.column_qdrant_repository.ensure_collection()

            points : list[dict] = []
            for column_info in column_infos:
                points.append({
                    'id' : uuid.uuid4(),
                    'embedding_text':column_info.name,
                    'payload':asdict(column_info)
                })
                points.append({
                    'id' : uuid.uuid4(),
                    'embedding_text':column_info.description,
                    'payload':asdict(column_info)
                })

                for alia in column_info.alias:
                    points.append({
                        'id' : uuid.uuid4(),
                        'embedding_text':alia,
                        'payload':asdict(column_info)
                    })
            
            # 批量向量化
            embedding_texts = [point['embedding_text'] for point in points]
            embedding_batch_size = 20
            embedding : list[list[float]] = []
            for i in range(0,len(embedding_texts),embedding_batch_size):
                batch_embedding_texts = embedding_texts[i:i+embedding_batch_size]
                batch_embeddings = await self.embedding_client.aembed_documents(batch_embedding_texts)
                embedding.extend(batch_embeddings)

            ids = [point['id'] for point in points]
            payloads = [point['payload'] for point in points]

            await self.column_qdrant_repository.upsert(ids,embedding,payloads)

            # 2.3 对指定的维度字段的取值建立全文索引
            await self.value_es_repository.ensure_index()

            value_infos: list[ValueInfo] = []
            for table in meta_config.tables:
                for column in table.columns:
                    if column.sync:
                        # 查询字段取值
                        current_column_values = await self.dw_mysql_repository.get_column_values(table.name,column.name,limit = 100000)
                        current_values_infos = [ValueInfo(id = f"{table.name}.{column.name}.{current_column_value}",value = current_column_value,
                                   column_id=f"{table.name}.{column.name}") for current_column_value in current_column_values]
                        value_infos.extend(current_values_infos)

            await self.value_es_repository.index(value_infos)

        # 3.根据配置文件同步指定的指标信息
        if meta_config.metrics:
            pass
            # 3.1 将指标信息保存meta数据库中

            # 3.2 对指标信息建立向量索引
