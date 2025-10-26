from document_database.mongo_setup import MongoDocumentStore

class MongoWriter:
    def __init__(self):
        self.store = MongoDocumentStore()

    def save(self, app_id: str, doc_id: str, structured_json: dict):
        self.store.insert_structured_data(app_id, doc_id, structured_json)