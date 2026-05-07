from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

class DWMySQLRepository:
    def __init__(self,session:AsyncSession):
        self.session = session
    async def get_column_types(self,table_name:str) -> dict:
        sql = f"show columns from {table_name}"
        result = await self.session.execute(text(sql))
        result_dict = result.mappings().fetchall()
        # [{Field:order_id,Type:varchar(30),Null:No},{Field:customer_id,Type:varchar(20),Null:Yes}]

        return {row['Field']: row['Type'] for row in result_dict}
        # {order_id:varchar(30),customer_id:varchar(30)}
        # 字段名：类型


    async def get_column_values(self,table_name:str,column_name:str,limit:int = 10) -> list:
        sql = f"select distinct {column_name} from {table_name} limit {limit}"
        result = await self.session.execute(text(sql))
        return [row[0] for row in result.fetchall()]
