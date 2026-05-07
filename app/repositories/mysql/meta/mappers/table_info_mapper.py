"""
实现table_info的orm实体和业务实体的转换
"""

from dataclasses import asdict

from app.models.table_info import TableInfoMySQL
from app.entities.table_info import TableInfo

class TableInfoMapper:
    @staticmethod
    def to_entity(table_info_mysql:TableInfoMySQL) -> TableInfo:
        return TableInfo(
            id = table_info_mysql.id,
            name = table_info_mysql.name,
            role = table_info_mysql.role,
            description= table_info_mysql.description
        )

    @staticmethod
    def to_model(table_info:TableInfo) -> TableInfoMySQL:
        # return TableInfoMySQL(
        #     id = table_info.id,
        #     name = table_info.name,
        #     role = table_info.role,
        #     description= table_info.description
        # )
        # 或者使用  dataclasses的asdict把对应的实体转换为字典，再使用**把字典解包为关键字参数作为传递
        return TableInfoMySQL(
            **asdict(table_info)
        )