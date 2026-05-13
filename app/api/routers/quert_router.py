from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from fastapi import Depends
from typing import Annotated
from app.services.query_service import QueryService
from app.api.schemas.query_schema import QuerySchema
from app.api.dependencies import get_query_service
query_router = APIRouter()


@query_router.post("/api/query")
async def query_handler(query: QuerySchema,query_service: Annotated[QueryService,Depends(get_query_service)]):

    return StreamingResponse(query_service.query(query.query),media_type="text/event-stream")
