from app.agent.state import  DataAgentState
from langgraph.runtime import Runtime
from app.agent.context import DataAgentContext
from datetime import date
from app.agent.state import DateInfoState,DBInfoState
from app.core.log import logger
async def add_extra_context(state:DataAgentState,runtime:Runtime[DataAgentContext]):
    writer= runtime.stream_writer
    writer({"type": "progress","step": "添加额外上下文","status": "running"})
    
    try:
        dw_mysql_repository = runtime.context["dw_mysql_repository"]

        today = date.today()
        data_str = today.strftime("%Y-%m-%d")
        weekday = today.strftime("%A")
        quarter = f"Q{(today.month-1) // 3 + 1}"
        data_info = DateInfoState(date=data_str,weekday=weekday,quarter=quarter)


        db = await dw_mysql_repository.get_db_info()

        db_info = DBInfoState(**db)

        writer({"type": "progress","step": "添加额外上下文","status": "success"})
        logger.info(f"数据库信息:{db_info}")
        logger.info(f"日期信息:{data_info}")

        return {
            "date_info":data_info,
            "db_info":db_info
        }
    except Exception as e:
        logger.error(f"添加额外上下文失败:{e}")
        writer({"type": "progress","step": "添加额外上下文","status": "error"})
        raise
