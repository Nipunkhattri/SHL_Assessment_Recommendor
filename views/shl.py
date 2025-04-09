from fastapi import APIRouter, HTTPException
from typing import List
from models.shlmodel import QueryRequest, QueryResponse, RecommendationResponse
from pipeline import AssessmentIndexer

shl_router = APIRouter(prefix="", tags=["SHL Recommendation"])

indexer = AssessmentIndexer()

type_mapping = {
    "A": "Ability & Aptitude",
    "B": "Biodata & Situational Judgement",
    "C": "Competencies",
    "D": "Development & 360",
    "E": "Assessment Exercises",
    "K": "Knowledge & Skills",
    "P": "Personality & Behavior",
    "S": "Simulations"
}

@shl_router.post("/recommend", response_model=RecommendationResponse)
async def query(request: QueryRequest):
    try:
        query_text = request.query
        if not query_text.strip():
            raise ValueError("Please provide a valid query")
        results = indexer.query(query_text)
        response = []
        
        for node in results:
            metadata = node.node.metadata
            test_types = metadata.get("TestTypes", [])
            mapped_types = [type_mapping.get(t, t) for t in test_types]
            response.append(QueryResponse(
                url=metadata.get("url", ""),
                adaptive_support=metadata.get("Adaptive/IRT Support", "No"),
                description=metadata.get("description", ""),
                duration=int(metadata.get("duration", "0").split()[0]),
                remote_support=metadata.get("RemoteTesting", "No"),
                test_type=mapped_types
            ))
        return RecommendationResponse(recommended_assessments=response)

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))