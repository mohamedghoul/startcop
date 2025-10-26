# main.py  –  BACKEND-ONLY  –  Objective 1 entry point
# ================================================
# 1. Replaces SQLite with MongoDB
# 2. Saves final structured JSON for Objective 2 vector DB
# 3. Starts 24-h KB scheduler (un-commented & safe)
# 4. Keeps temp-file hygiene & env-based config

import os
import json
import tempfile
import shutil
import threading
from pathlib import Path
from datetime import datetime

from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import JSONResponse

from document_processor.extractor import DocumentIntelligenceEngine
from knowledge_base.gap_analyzer import GapAnalyzer
from document_database.mongo_setup import MongoDocumentStore   # NEW
from processing_pipeline.mongo_writer import MongoWriter       # NEW
from knowledge_base.update_scheduler import start_scheduler    # NEW

# ------------------------------------------------------------------
# Env-based configuration (see config.py for defaults / overrides)
# ------------------------------------------------------------------
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
kb_path   = REPO_ROOT / "backend" / "src" / os.getenv("KB_PATH", "real_qcb_regulations.json")
res_path  = REPO_ROOT / "backend" / "src" / os.getenv("RES_PATH", "resource_mapping_data.json")
MONGO_URI     = os.getenv("MONGO_URI", "mongodb://localhost:27017")

# ------------------------------------------------------------------
# App singletons
# ------------------------------------------------------------------
app = FastAPI(title="QCB Regulatory Navigator Phase-1")

engine   = DocumentIntelligenceEngine()
gapper   = GapAnalyzer(kb_path=str(kb_path), resource_path=str(res_path))
mongo    = MongoDocumentStore()          # MongoDB access
writer   = MongoWriter()                 # Thin wrapper to push JSON -> Mongo

# ------------------------------------------------------------------
# Health checks
# ------------------------------------------------------------------
@app.get("/kb/status")
def kb_status():
    if not kb_path.exists():
        return JSONResponse(content={"last_updated": None, "article_count": 0}, status_code=200)
    meta = json.loads(kb_path.read_text(encoding="utf-8"))["metadata"]
    return JSONResponse(content={"last_updated": meta["scraped_at"], "article_count": meta["total_regulations"]})

@app.get("/health")
def health():
    return {"status": "ok", "mongo": mongo.is_alive()}

# ------------------------------------------------------------------
# Core endpoint – Objective 1 fulfilled here
# ------------------------------------------------------------------
@app.post("/apply")
async def apply_fintech(
    startup_name: str = Form(...),
    application_type: str = Form(...),
    files: list[UploadFile] = File(...)
):
    """
    1. Store uploaded files temporarily
    2. Run document intelligence pipeline
    3. Persist structured JSON -> MongoDB (for Objective 2 vector DB)
    4. Return gaps + application ID
    """
    tmpdir = tempfile.mkdtemp()
    try:
        docs = []
        for f in files:
            path = Path(tmpdir) / f.filename
            with open(path, "wb") as buffer:
                shutil.copyfileobj(f.file, buffer)
            docs.append({
                "type": f.filename.split(".")[0],
                "path": str(path),
                "size": path.stat().st_size
            })

        # Insert application & documents into Mongo
        app_id = mongo.create_application(startup_name, application_type, docs)

        results = []
        for doc in docs:
            # >>>  DEBUG  <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
            from document_processor.parser import DocumentParser
            raw_text = DocumentParser().parse_document(doc["path"])
            print(f"=== TEXT LEN {len(raw_text)}  FIRST 800 chars ===")
            print(raw_text[:800])
            print("=== END TEXT ======================================")
            # >>>  END DEBUG  <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<

            res = engine.process_document(doc["path"])
            # >>>  DEBUG  <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
            print(f"=== EXTRACTED METRICS COUNT: {len(res.entities.financial_metrics)} ===")
            for m in res.entities.financial_metrics:
                print(m.model_dump())
            print("=== END METRICS =====================================")
            # >>>  END DEBUG  <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<

            gaps = gapper.find_gaps(res.entities)

            # Persist structured output for Objective 2
            doc_id = mongo.save_document_result(app_id, doc["type"], res.dict())

            results.append({
                "document": doc["type"],
                "gaps": [g.dict() for g in gaps],
                "mongo_doc_id": doc_id
            })

        return {"application_id": app_id, "results": results}

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)

# ------------------------------------------------------------------
# Startup hooks
# ------------------------------------------------------------------
@app.on_event("startup")
def boot_scheduler():
    """Start 24-h knowledge-base refresh in daemon thread"""
    threading.Thread(target=start_scheduler, daemon=True).start()
