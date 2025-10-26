"""
Script to generate and populate test data for ChromaDB and MongoDB, using hackathon mock document formats.
Test data is stored in separate collections/databases to avoid mixing with production data.
Run with the --test flag to populate test data.
"""

import argparse
import os
import logging
import json
import re
from pathlib import Path
from pymongo import MongoClient
import chromadb
from chromadb.config import Settings

import sys

print(f"__file__ = {__file__}")
print(f"Path(__file__).parent = {Path(__file__).parent}")
import os

print(f"os.getcwd() = {os.getcwd()}")

regulatory_chunks = []
QCB_REG_PATH = (Path(__file__).parent / "../real_qcb_regulations.json").resolve()
with open(QCB_REG_PATH, "r", encoding="utf-8") as f:
    qcb_data = json.load(f)
regulations = qcb_data.get("regulations", {})
for category, regs in regulations.items():
    for reg in regs:
        # Use title and content if available, else skip
        title = reg.get("title", "")
        content = reg.get("content", "")
        if not content:
            continue
        # Chunk by paragraphs (double newline or section/article markers)
        # Try to split by Article/Section/Chapter if present, else by paragraphs
        chunks = re.split(r"(Article \d+\.\d+|Section \d+|Chapter \d+|\n\n)", content)
        # Recombine so each chunk includes its heading if split by marker
        chunk_list = []
        i = 0
        while i < len(chunks):
            if re.match(r"Article \d+\.\d+|Section \d+|Chapter \d+", chunks[i]):
                heading = chunks[i].strip()
                text = chunks[i + 1].strip() if i + 1 < len(chunks) else ""
                chunk_text = f"{heading} {text}".strip()
                if chunk_text:
                    chunk_list.append(chunk_text)
                i += 2
            else:
                text = chunks[i].strip()
                if text:
                    chunk_list.append(text)
                i += 1
        # Fallback: if no chunks, use the whole content
        if not chunk_list:
            chunk_list = [content.strip()]
        for idx, chunk in enumerate(chunk_list):
            chunk_id = f"{category}_{title.replace(' ', '_')}_{idx+1}"
            regulatory_chunks.append(
                {
                    "id": chunk_id,
                    "text": chunk,
                    "metadata": {
                        "category": category,
                        "title": title,
                        "source_file": "real_qcb_regulations.json",
                        "chunk_index": idx + 1,
                    },
                }
            )
        for category, regs in regulations.items():
            for reg in regs:
                # Use title and content if available, else skip
                title = reg.get("title", "")
                content = reg.get("content", "")
                if not content:
                    continue
                # Chunk by paragraphs (double newline or section/article markers)
                import re

                # Try to split by Article/Section/Chapter if present, else by paragraphs
                chunks = re.split(
                    r"(Article \d+\.\d+|Section \d+|Chapter \d+|\n\n)", content
                )
                # Recombine so each chunk includes its heading if split by marker
                chunk_list = []
                i = 0
                while i < len(chunks):
                    if re.match(r"Article \d+\.\d+|Section \d+|Chapter \d+", chunks[i]):
                        heading = chunks[i].strip()
                        text = chunks[i + 1].strip() if i + 1 < len(chunks) else ""
                        chunk_text = f"{heading} {text}".strip()
                        if chunk_text:
                            chunk_list.append(chunk_text)
                        i += 2
                    else:
                        text = chunks[i].strip()
                        if text:
                            chunk_list.append(text)
                        i += 1
                # Fallback: if no chunks, use the whole content
                if not chunk_list:
                    chunk_list = [content.strip()]
                for idx, chunk in enumerate(chunk_list):
                    chunk_id = f"{category}_{title.replace(' ', '_')}_{idx+1}"
                    regulatory_chunks.append(
                        {
                            "id": chunk_id,
                            "text": chunk,
                            "metadata": {
                                "category": category,
                                "title": title,
                                "source_file": "real_qcb_regulations.json",
                                "chunk_index": idx + 1,
                            },
                        }
                    )


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
        # Wipe the collection before inserting new data
        try:
            chroma_client.delete_collection(collection_name)
            logging.info(
                f"Deleted existing ChromaDB collection '{collection_name}' to prevent duplicates."
            )
        except Exception:
            pass  # Collection may not exist yet
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
        # Wipe the regulations collection before inserting new data
        collection_name = "regulations_test" if is_test else "regulations"
        db[collection_name].delete_many({})
        logging.info(
            f"Deleted all documents from MongoDB collection '{collection_name}' to prevent duplicates."
        )

        # Validate documents against schema (for dev/debug only)
        def validate(doc, schema):
            for k, v in schema.items():
                if k not in doc:
                    raise ValueError(f"Missing key '{k}' in document: {doc}")

        for doc in [startup_business_plan, startup_privacy_policy, startup_articles]:
            # validate(doc, STARTUP_DOCUMENT_SCHEMA)
            pass
        # validate(resource_mapping, RESOURCE_MAPPING_SCHEMA)
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
