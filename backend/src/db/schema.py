"""
MongoDB and ChromaDB schema definitions for StartCop backend.
This file defines the expected structure for each collection and ChromaDB collection metadata.
"""

# MongoDB Schemas (for documentation and validation)
STARTUP_DOCUMENT_SCHEMA = {
    "company_name": str,
    "document_type": str,  # e.g., 'business_plan', 'privacy_policy', 'articles_of_association'
    "text": str,
    "metadata": dict,  # e.g., {"source_file": str, "date": str}
}

RESOURCE_MAPPING_SCHEMA = {
    "qdb_programs": [
        {
            "program_id": str,
            "program_name": str,
            "focus_areas": list,
            "eligibility": str,
        }
    ],
    "compliance_experts": [
        {
            "expert_id": str,
            "name": str,
            "specialization": str,
            "contact": str,
        }
    ],
}

# ChromaDB Collection Schema (for documentation)
CHROMA_REGULATIONS_SCHEMA = {
    "id": str,  # unique chunk/document id
    "embedding": list,  # vector embedding
    "document": str,  # text chunk
    "metadata": {
        "source_file": str,
        "section": str,
        "article": str,
        # ...other regulatory metadata
    },
}

# Note: These are not enforced by MongoDB/ChromaDB, but can be used for validation or with ODMs.
