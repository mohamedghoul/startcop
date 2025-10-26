from fastapi import FastAPI, UploadFile, File, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from rag.pipeline import RAGPipeline

app = FastAPI(title="StartCop API", description="API for StartCop, the AI Regulatory Navigator", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

rag_pipeline = RAGPipeline(collection_name="regulations_test")

class RAGQuery(BaseModel):
    query: str
    top_k: int = 3


from fastapi.responses import JSONResponse

@app.get("/api/v0", response_class=JSONResponse)
def read_root() -> dict:
    return {"message": "StartCop API Version 0 is running."}


@app.post("/api/v0/upload/", response_class=JSONResponse)
async def upload_document(file: UploadFile = File(...)) -> dict:
    # TODO Save the file in the database
    content = await file.read()
    filename = file.filename
    # TODO Trigger ingestion and processing of the uploaded document
    return {"filename": file.filename, "size": len(content), "message": "File uploaded successfully."}


@app.post("/api/v0/rag/", response_class=JSONResponse)
def run_rag(query: RAGQuery, with_scorecard: bool = Query(False, description="Include readiness scorecard")) -> dict:
    """Run the RAG pipeline with a user query and return explanation and relevant regulations. Optionally include readiness scorecard."""
    result = rag_pipeline.run(query.query, top_k=query.top_k, with_scorecard=with_scorecard)
    return result