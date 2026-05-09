from app.repositories.mysql.meta.meta_mysql_repository import MetaMySQLRepository
from typing import TypedDict
from app.entities.column_info import ColumnInfo
from app.entities.metric_info import MetricInfo
from app.entities.value_info import ValueInfo

class MetricInfoState(TypedDict):
    name: str
    description: str
    relevant_columns: list[str]
    alias: list[str]


class ColumnInfoState(TypedDict):
    name: str
    type: str
    role: str
    examples: list
    description: str
    alias: list[str]


class TableInfoState(TypedDict):
    name: str
    role: str
    description: str
    columns: list[ColumnInfoState]


class DateInfoState(TypedDict):
    date: str
    weekday: str
    quarter: str

class DBInfoState(TypedDict):
    dialect: str
    version: str

class DataAgentState(TypedDict):
    
    query: str # 用户的原始查询语句
    keywords : list[str]  # 抽取的关键词

    retrieved_column_infos : list[ColumnInfo] # 从向量数据库中检索到的字段信息
    retrieved_metric_infos : list[MetricInfo] # 从向量数据库中检索到的指标信息
    retrieved_value_infos : list[ValueInfo] # 从ES中检索到的字段值信息

    table_infos : list[TableInfoState] # 表信息
    metric_infos : list[MetricInfoState] # 指标信息

    date_info: DateInfoState # 数据库信息
    db_info: DBInfoState # 日期信息

    sql: str # 生成的sql

    error: str | None # 校验SQL时出现的错误信息

