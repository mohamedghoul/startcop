import pytest
import logging
from ...src.rag.pipeline import RAGPipeline


@pytest.fixture(scope="session")
def rag_pipeline():
    """Session-wide RAGPipeline fixture for all tests."""
    return RAGPipeline(collection_name="regulations_test")


@pytest.fixture(autouse=True, scope="session")
def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[logging.StreamHandler()],
    )
    logging.info("Pytest session started. All test logs will appear below.")
    yield
    logging.info("Pytest session finished.")
