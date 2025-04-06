from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse
from pipeline import AssessmentIndexer
from typing import List
from models.shlmodel import QueryRequest, QueryResponse

shl_router = APIRouter(prefix="/api/v1/shl", tags=["SHL Recommendation"])

indexer = AssessmentIndexer()

@shl_router.post("/query", response_model=List[QueryResponse])
async def query(request: QueryRequest):
    try:
        query_text = request.query
        results = indexer.query(query_text)
        response = []
        for node in results:
            response.append(QueryResponse(
                text=node.node.text,
                score=node.score,
                metadata=node.node.metadata
            ))
        return response

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))