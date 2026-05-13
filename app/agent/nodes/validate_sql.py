from app.agent.state import  DataAgentState
from langgraph.runtime import Runtime
from app.agent.context import DataAgentContext
from app.repositories.mysql.dw.dw_mysql_repository import DWMySQLRepository
from app.core.log import logger
async def validate_sql(state:DataAgentState,runtime:Runtime[DataAgentContext]):

    writer= runtime.stream_writer
    writer({"type": "progress","step": "验证SQL","status": "running"})
    
    sql = state["sql"]
    dw_mysql_repository = runtime.context["dw_mysql_repository"]
    try:
        try:
            await dw_mysql_repository.validate(sql)
            writer({"type": "progress","step": "验证SQL","status": "success"})
            logger.info("SQL语法正确")
            return {"error":None}
        except Exception as e:
            logger.info(f"SQL语法错误:{str(e)}")
            writer({"type": "progress","step": "验证SQL","status": "error"})
            return {"error":str(e)}
    except Exception as e:
        logger.error(f"验证SQL失败:{e}")
        writer({"type": "progress","step": "验证SQL","status": "error"})
        raise
    


    
