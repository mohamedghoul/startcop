"""
Complete Document Processing Pipeline for Phase 1
Optimized for performance and efficiency
"""

import time
import logging
from typing import Dict, List, Optional, Any
from pathlib import Path
import asyncio
import aiofiles
from concurrent.futures import ThreadPoolExecutor
import psutil
import gc


# Use the real document processor extractors
from src.document_processor.extractor import DocumentIntelligenceEngine
from src.document_processor.models import ProcessingResult

logger = logging.getLogger(__name__)


class ProcessingPipeline:
    """
    Complete document processing pipeline with performance optimization
    Uses async processing and memory management for efficiency
    """

    def __init__(self, max_workers: int = 4):
        self.max_workers = max_workers
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.doc_engine = DocumentIntelligenceEngine()
        # Performance optimization settings
        self.chunk_size = 1024 * 1024  # 1MB chunks for large files
        self.memory_limit = 80  # 80% memory usage limit
        self.batch_size = 10  # Process documents in batches

    async def process_application_documents(
        self, application_id: int, document_paths: List[str]
    ) -> List[Dict[str, Any]]:
        """
        Process all documents for an application with performance optimization
        """
        logger.info(
            f"[CHECKPOINT] Starting processing pipeline for application {application_id}"
        )
        start_time = time.time()

        # Monitor system resources
        initial_memory = psutil.virtual_memory().percent
        logger.info(f"[DATA] Initial memory usage: {initial_memory}%")

        results = []

        # Process in batches for memory efficiency
        for i in range(0, len(document_paths), self.batch_size):
            batch = document_paths[i : i + self.batch_size]
            logger.info(
                f"[CHECKPOINT] Processing batch {i // self.batch_size + 1}: {batch}"
            )
            batch_results = await self._process_batch(application_id, batch)
            logger.info(f"[DATA] Batch results: {batch_results}")
            results.extend(batch_results)

            # Force garbage collection after each batch
            gc.collect()

            # Check memory usage
            current_memory = psutil.virtual_memory().percent
            if current_memory > self.memory_limit:
                logger.warning(f"Memory usage high: {current_memory}%")
                # Brief pause to allow memory cleanup
                await asyncio.sleep(0.1)

        total_time = time.time() - start_time

        # Performance analysis
        self.performance_monitor.record_batch_processing(
            len(document_paths), total_time, initial_memory
        )

        logger.info(
            f"Completed processing {len(document_paths)} documents in {total_time:.2f}s"
        )

        return results

    async def _process_batch(
        self, application_id: int, document_paths: List[str]
    ) -> List[Dict[str, Any]]:
        """Process a batch of documents concurrently"""
        logger.info(
            f"[CHECKPOINT] Starting batch processing for application {application_id} with {len(document_paths)} documents"
        )
        tasks = []
        for doc_path in document_paths:
            logger.info(f"[CHECKPOINT] Scheduling document: {doc_path}")
            task = self._process_single_document(application_id, doc_path)
            tasks.append(task)
        results = await asyncio.gather(*tasks, return_exceptions=True)
        valid_results = [r for r in results if not isinstance(r, Exception)]
        logger.info(f"[DATA] Batch valid results: {valid_results}")
        return valid_results

    async def _process_single_document(
        self, application_id: int, document_path: str
    ) -> Dict[str, Any]:
        """Process a single document with full pipeline"""
        doc_start_time = time.time()
        logger.info(f"[CHECKPOINT] Processing single document: {document_path}")
        try:
            # Step 1: Process document using DocumentIntelligenceEngine
            logger.info(
                f"[CHECKPOINT] Running DocumentIntelligenceEngine on {document_path}"
            )
            result: ProcessingResult = await asyncio.get_event_loop().run_in_executor(
                self.executor, self.doc_engine.process_document, document_path
            )
            logger.info(f"[DATA] ProcessingResult: {result}")
            # Convert result to dict for API compatibility
            import dataclasses

            result_dict = (
                dataclasses.asdict(result)
                if hasattr(result, "__dataclass_fields__")
                else dict(result)
            )
            result_dict.update(
                {
                    "document_path": document_path,
                    "processing_time": time.time() - doc_start_time,
                    "status": "completed",
                }
            )
            logger.info(
                f"[CHECKPOINT] Finished processing {document_path} in {result_dict['processing_time']:.2f}s"
            )
            return result_dict
        except Exception as e:
            logger.error(
                f"[ERROR] Error processing document {document_path}: {e}", exc_info=True
            )
            return {
                "document_path": document_path,
                "status": "error",
                "error": str(e),
                "processing_time": time.time() - doc_start_time,
            }

    # Quality check and text extraction are now handled by DocumentIntelligenceEngine

    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get comprehensive performance metrics"""
        # Placeholder: add your own performance tracking logic if needed
        cpu_percent = psutil.cpu_percent(interval=1)
        memory_info = psutil.virtual_memory()
        disk_io = psutil.disk_io_counters()
        metrics = {
            "system_performance": {
                "cpu_usage": cpu_percent,
                "memory_usage": memory_info.percent,
                "available_memory_gb": memory_info.available / (1024**3),
                "disk_read_mb": disk_io.read_bytes / (1024**2),
                "disk_write_mb": disk_io.write_bytes / (1024**2),
            },
            "optimization_settings": {
                "max_workers": self.max_workers,
                "chunk_size": self.chunk_size,
                "batch_size": self.batch_size,
                "memory_limit": self.memory_limit,
            },
        }
        logger.info(f"[DATA] Performance metrics: {metrics}")
        return metrics

    def optimize_performance(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Auto-optimize based on performance metrics"""
        recommendations = {}

        # Optimize worker count based on CPU usage
        if metrics["system_performance"]["cpu_usage"] > 80:
            recommendations["reduce_workers"] = max(1, self.max_workers - 1)
        elif metrics["system_performance"]["cpu_usage"] < 30:
            recommendations["increase_workers"] = min(8, self.max_workers + 1)

        # Optimize batch size based on memory usage
        if metrics["system_performance"]["memory_usage"] > self.memory_limit:
            recommendations["reduce_batch_size"] = max(5, self.batch_size - 2)

        # Optimize chunk size based on processing time
        avg_time_per_doc = metrics.get("avg_processing_time_per_document", 0)
        if avg_time_per_doc > 5:  # If taking too long per document
            recommendations["reduce_chunk_size"] = max(512 * 1024, self.chunk_size // 2)

        return recommendations
