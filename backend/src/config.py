import os
from pathlib import Path

BACKEND_DIR = Path(__file__).parent.parent

# Mongo
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME   = os.getenv("DB_NAME", "regulatory_navigator")

# KB & resources
KB_PATH  = BACKEND_DIR / os.getenv("KB_PATH", "real_qcb_regulations.json")
RES_PATH = BACKEND_DIR / os.getenv("RES_PATH", "resource_mapping_data.json")

# Processing
MAX_WORKERS        = int(os.getenv("MAX_WORKERS", "4"))
MEMORY_LIMIT_PERCENT = int(os.getenv("MEMORY_LIMIT", "80"))