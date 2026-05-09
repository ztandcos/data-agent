from app.repositories.qdrant.column_qdrant_repository import ColumnQdrantRepository
from typing import TypedDict
from app.clients.embedding_client_manager import TextEmbeddingsInferenceEmbeddings
from app.repositories.qdrant.metric_qdrant_repository import MetricQdrantRepository
from app.repositories.es.value_es_repository import ValueESRepository
from app.repositories.mysql.meta.meta_mysql_repository import MetaMySQLRepository
from app.repositories.mysql.dw.dw_mysql_repository import DWMySQLRepository
class DataAgentContext(TypedDict):
    column_repository: ColumnQdrantRepository
    embedding_client: TextEmbeddingsInferenceEmbeddings
    metric_qdrant_repository: MetricQdrantRepository
    value_es_repository: ValueESRepository
    meta_mysql_repository: MetaMySQLRepository
    dw_mysql_repository: DWMySQLRepository

    