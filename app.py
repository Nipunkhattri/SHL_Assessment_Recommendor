from fastapi import FastAPI, status, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from views.shl import shl_router
from contextlib import asynccontextmanager
from pipeline import AssessmentIndexer

@asynccontextmanager
async def lifespan(app: FastAPI):
    json_file_path = r".\assessments.json"
    indexer = AssessmentIndexer()
    indexer.create_index(json_file_path)
    yield

app = FastAPI(lifespan=lifespan)

origins = [
    "https://nipunkhattri-shl-assessment-recommendor-streamlit-bfh1ad.streamlit.app/"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(shl_router)

@app.get("/", status_code=status.HTTP_200_OK)
async def root():
    return {"message": "Welcome to the SHL Assessment API"}