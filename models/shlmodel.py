from pydantic import BaseModel

class QueryRequest(BaseModel):
    query: str

class QueryResponse(BaseModel):
    text: str
    score: float
    metadata: dict