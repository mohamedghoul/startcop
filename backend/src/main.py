from fastapi import FastAPI, UploadFile, File, Query, Form
from fastapi.middleware.cors import CORSMiddleware
from dataclasses import dataclass
from src.rag.pipeline import RAGPipeline
from fastapi.responses import JSONResponse
import os
import dataclasses
import json
import tempfile
import shutil
import threading
from pathlib import Path
from src.document_processor.extractor import DocumentIntelligenceEngine
from src.knowledge_base.gap_analyzer import GapAnalyzer
from src.document_database.mongo_setup import MongoDocumentStore
from src.processing_pipeline.mongo_writer import MongoWriter
from src.knowledge_base.update_scheduler import start_scheduler

app = FastAPI(
    title="StartCop API",
    description="API for StartCop, the AI Regulatory Navigator",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

rag_pipeline = RAGPipeline(collection_name="regulations_test")


@dataclass
class RAGQuery:
    query: str
    top_k: int = 3


# Env/config for Objective 1
SRC_DIR = Path(__file__).parent
kb_path = SRC_DIR / os.getenv("KB_PATH", "real_qcb_regulations.json")
res_path = SRC_DIR / os.getenv("RES_PATH", "resource_mapping_data.json")
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")

engine = DocumentIntelligenceEngine()
gapper = GapAnalyzer(kb_path=str(kb_path), resource_path=str(res_path))
mongo = MongoDocumentStore()
writer = MongoWriter()


@app.get("/api/v0", response_class=JSONResponse)
def read_root() -> dict:
    return {"message": "StartCop API Version 0 is running."}


@app.post("/api/v0/upload/", response_class=JSONResponse)
async def upload_and_apply(
    startup_name: str = Form(...),
    application_type: str = Form(...),
    files: list[UploadFile] = File(...),
) -> dict:
    """
    Unified endpoint: Upload files, process documents, persist to MongoDB, return gaps + application ID.
    """
    import logging

    logger = logging.getLogger("startcop.main")
    print("UPLOAD HIT", flush=True)
    logger.info(
        f"Received upload: startup_name={startup_name}, application_type={application_type}, files={[f.filename for f in files]}"
    )
    tmpdir = tempfile.mkdtemp()
    try:
        docs = []
        for f in files:
            path = Path(tmpdir) / f.filename
            with open(path, "wb") as buffer:
                shutil.copyfileobj(f.file, buffer)
            logger.info(
                f"Saved uploaded file {f.filename} to {path} (size={path.stat().st_size})"
            )
            docs.append(
                {
                    "type": f.filename.split(".")[0],
                    "path": str(path),
                    "size": path.stat().st_size,
                }
            )
        logger.info(
            f"Creating application in MongoDB for startup_name={startup_name}, application_type={application_type}"
        )
        app_id = mongo.create_application(startup_name, application_type, docs)
        logger.info(f"Created application_id={app_id}")
        results = []
        for doc in docs:
            logger.info(f"Processing document: {doc['type']} at {doc['path']}")
            res = engine.process_document(doc["path"])
            logger.info(f"Extraction result for {doc['type']}: {res.entities}")
            gaps = gapper.find_gaps(res.entities)
            logger.info(f"Gap analysis for {doc['type']}: {gaps}")
            doc_id = mongo.save_document_result(
                app_id, doc["type"], dataclasses.asdict(res)
            )
            logger.info(f"Written to MongoDB with doc_id={doc_id}")
            results.append(
                {
                    "document": doc["type"],
                    "gaps": [dataclasses.asdict(g) for g in gaps],
                    "mongo_doc_id": doc_id,
                }
            )
        logger.info(f"Returning application_id={app_id} with {len(results)} results.")
        return {"application_id": app_id, "results": results}
    except Exception as e:
        logger.error(f"Error in upload_and_apply: {e}")
        return JSONResponse(content={"error": str(e)}, status_code=500)
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)
        logger.info(f"Cleaned up temp dir {tmpdir}")


@app.post("/api/v0/rag/", response_class=JSONResponse)
def run_rag(
    query: RAGQuery,
    with_scorecard: bool = Query(False, description="Include readiness scorecard"),
) -> dict:
    """Run the RAG pipeline with a user query and return explanation and relevant regulations. Optionally include readiness scorecard."""
    result = rag_pipeline.run(
        query.query, top_k=query.top_k, with_scorecard=with_scorecard
    )
    return result


@app.get("/kb/status", response_class=JSONResponse)
def kb_status():
    if not kb_path.exists():
        return {"last_updated": None, "article_count": 0}
    meta = json.loads(kb_path.read_text(encoding="utf-8"))["metadata"]
    return {
        "last_updated": meta["scraped_at"],
        "article_count": meta["total_regulations"],
    }


@app.get("/health", response_class=JSONResponse)
def health():
    return {"status": "ok", "mongo": mongo.is_alive()}


@app.on_event("startup")
def boot_scheduler():
    """Start 24-h knowledge-base refresh in daemon thread"""
    threading.Thread(target=start_scheduler, daemon=True).start()
