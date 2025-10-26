from pymongo import MongoClient
from typing import Dict, List
import os
from datetime import datetime

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = "regulatory_navigator"

class MongoDocumentStore:
    def __init__(self):
        try:
            self.client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=2000)
            self.client.admin.command('ping')  # quick check
        except Exception:
            print("⚠️  Mongo not reachable – using RAM fallback")
            from pymongo import MongoClient
            from mongomock import MongoClient as MockClient
            self.client = MockClient()  # in-memory, API-identical
        self.db = self.client[DB_NAME]
        self.startups = self.db["startups"]
        self.applications = self.db["applications"]
        self.documents = self.db["documents"]
        self.structured_data = self.db["structured_data"]  # for Objective 2 vector DB

    def insert_structured_data(self, app_id: str, doc_id: str, payload: dict):
        self.structured_data.insert_one({
            "app_id": app_id,
            "doc_id": doc_id,
            "payload": payload,
            "timestamp": datetime.utcnow()
        })

    def create_application(self, startup_name: str, app_type: str, docs: List[Dict]) -> str:
        app_doc = {
            "startup_name": startup_name,
            "application_type": app_type,
            "documents": docs,
            "created_at": datetime.utcnow()
        }
        return str(self.applications.insert_one(app_doc).inserted_id)

    def save_document_result(self, app_id: str, doc_type: str, payload: Dict) -> str:
        rec = {
            "app_id": app_id,
            "doc_type": doc_type,
            "payload": payload,
            "timestamp": datetime.utcnow()
        }
        return str(self.structured_data.insert_one(rec).inserted_id)

    def is_alive(self) -> bool:
        return self.client.admin.command("ping").get("ok") == 1.0    