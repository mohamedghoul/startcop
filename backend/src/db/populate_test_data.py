"""
Script to generate and populate test data for ChromaDB and MongoDB, using hackathon mock document formats.
Test data is stored in separate collections/databases to avoid mixing with production data.
Run with the --test flag to populate test data.
"""

import argparse
import os
import logging
from src.db.schema import (
    STARTUP_DOCUMENT_SCHEMA,
    RESOURCE_MAPPING_SCHEMA,
    CHROMA_REGULATIONS_SCHEMA,
)
from pymongo import MongoClient
import chromadb
from chromadb.config import Settings

# --- Test Data (from hackathon mock documents) ---
# Regulatory data (chunked by article/section)
regulatory_chunks = [
    {
        "id": "qcb_aml_1.1.1",
        "text": "Article 1.1.1. Mandatory Verification: All regulated Fintech entities must implement enhanced Customer Due Diligence (CDD) procedures for any user transacting more than QAR 10,000 per calendar month.",
        "metadata": {
            "source_file": "qcb_aml_data_protection_regulation.md",
            "section": "1.1",
            "article": "1.1.1",
        },
    },
    {
        "id": "qcb_aml_2.1.1",
        "text": "Article 2.1.1. Data Residency: All customer personal identifiable information (PII) and transactional data related to Qatari citizens and residents must be stored on servers physically located within the State of Qatar.",
        "metadata": {
            "source_file": "qcb_aml_data_protection_regulation.md",
            "section": "2.1",
            "article": "2.1.1",
        },
    },
    {
        "id": "qcb_aml_2.2.1",
        "text": "Article 2.2.1. Compliance Officer: The entity must appoint a designated, independent Compliance Officer whose CV and credentials must be submitted to the QCB for approval prior to licensing.",
        "metadata": {
            "source_file": "qcb_aml_data_protection_regulation.md",
            "section": "2.2",
            "article": "2.2.1",
        },
    },
    {
        "id": "qcb_fintech_1.2.2",
        "text": "Article 1.2.2. Marketplace Lending (Category 2): Minimum regulatory capital of QAR 7,500,000 must be maintained at all times.",
        "metadata": {
            "source_file": "qcb_fintech_licensing_pathways.md",
            "section": "1.2",
            "article": "1.2.2",
        },
    },
]

# Startup business plan (as a single document)
startup_business_plan = {
    "company_name": "Al-Ameen Digital, LLC",
    "document_type": "business_plan",
    "text": """Project Al-Ameen: Peer-to-Peer Investment Platform\nDate: 2025-10-20\nCompany Name: Al-Ameen Digital, LLC\n... (rest of business plan as in mock data) ...""",
    "metadata": {"source_file": "fintech_startup_draft.md", "date": "2025-10-20"},
}

# Startup privacy policy
startup_privacy_policy = {
    "company_name": "Al-Ameen Digital, LLC",
    "document_type": "privacy_policy",
    "text": """Al-Ameen Digital: Data Privacy and Customer Consent Policy\nPolicy Owner: Head of Technology\n... (rest of privacy policy as in mock data) ...""",
    "metadata": {"source_file": "startup_data_privacy_policy.md", "date": "2025-09-01"},
}

# Articles of Association
startup_articles = {
    "company_name": "Al-Ameen Digital, LLC",
    "document_type": "articles_of_association",
    "text": """Al-Ameen Digital, LLC: Articles of Association (Excerpt)\nDate of Incorporation: 2025-07-01\n... (rest of articles as in mock data) ...""",
    "metadata": {
        "source_file": "startup_articles_of_association_mock.md",
        "date": "2025-07-01",
    },
}

# Resource mapping data (JSON)
resource_mapping = {
    "qdb_programs": [
        {
            "program_id": "QDB_INCUBATOR_001",
            "program_name": "Fintech Regulatory Accelerator",
            "focus_areas": [
                "Licensing Strategy",
                "Corporate Structure",
                "QCB Engagement",
            ],
            "eligibility": "Pre-license stage startups",
        },
        {
            "program_id": "QDB_EXPERT_002",
            "program_name": "AML Compliance Workshop Series",
            "focus_areas": [
                "AML Policy Drafting",
                "Transaction Monitoring",
                "FATF Compliance",
            ],
            "eligibility": "Startups with high-risk profile",
        },
    ],
    "compliance_experts": [
        {
            "expert_id": "EXPERT_C101",
            "name": "Dr. Aisha Al-Mansoori",
            "specialization": "Data Residency and Cloud Compliance (QCB Article 2.1)",
            "contact": "a.mansoori@compliancefirm.qa",
        },
        {
            "expert_id": "EXPERT_C102",
            "name": "Mr. Karim Hassan",
            "specialization": "AML/CFT Policy Drafting and Training (QCB Article 1.1.4)",
            "contact": "k.hassan@amlconsulting.qa",
        },
    ],
}


# --- Embedding function (dummy for now) ---
def dummy_embed(text):
    # Returns a fixed-size zero vector (replace with real model)
    return [0.0] * 384


# --- Main population script ---
def populate_chromadb(is_test=True):
    try:
        chroma_client = chromadb.HttpClient(
            host=os.environ.get("CHROMA_HOST", "localhost"),
            port=int(os.environ.get("CHROMA_PORT", 8000)),
            settings=Settings(allow_reset=True),
        )
        collection_name = "regulations_test" if is_test else "regulations"
        collection = chroma_client.get_or_create_collection(collection_name)
        for chunk in regulatory_chunks:
            collection.upsert(
                ids=[chunk["id"]],
                embeddings=[dummy_embed(chunk["text"])],
                documents=[chunk["text"]],
                metadatas=[chunk["metadata"]],
            )
        logging.info(
            f"Inserted {len(regulatory_chunks)} regulatory chunks into ChromaDB collection '{collection_name}'"
        )
    except Exception as e:
        logging.error(f"Failed to connect or upsert to ChromaDB: {e}")


def populate_mongodb(is_test=True):
    try:
        mongo_uri = os.environ.get("MONGO_URI", "mongodb://localhost:27017")
        db_name = "startcop_test" if is_test else "startcop"
        client = MongoClient(mongo_uri)
        db = client[db_name]

        # Validate documents against schema (for dev/debug only)
        def validate(doc, schema):
            for k, v in schema.items():
                if k not in doc:
                    raise ValueError(f"Missing key '{k}' in document: {doc}")

        for doc in [startup_business_plan, startup_privacy_policy, startup_articles]:
            validate(doc, STARTUP_DOCUMENT_SCHEMA)
        validate(resource_mapping, RESOURCE_MAPPING_SCHEMA)
        db.startup_documents.insert_many(
            [startup_business_plan, startup_privacy_policy, startup_articles]
        )
        db.resource_mapping.insert_one(resource_mapping)
        logging.info(
            f"Inserted startup docs and resource mapping into MongoDB database '{db_name}'"
        )
    except Exception as e:
        logging.error(f"Failed to connect or insert to MongoDB: {e}")


def main():
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s"
    )
    parser = argparse.ArgumentParser(
        description="Populate test or production data for ChromaDB and MongoDB."
    )
    parser.add_argument(
        "--test",
        action="store_true",
        help="Populate test data (default: production data)",
    )
    args = parser.parse_args()
    is_test = args.test
    populate_chromadb(is_test)
    populate_mongodb(is_test)
    logging.info("Data population complete.")


if __name__ == "__main__":
    main()
