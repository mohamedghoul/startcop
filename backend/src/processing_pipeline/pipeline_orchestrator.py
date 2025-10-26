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

from .text_extractor import AdvancedTextExtractor
from .quality_checker import DocumentQualityChecker
from .performance_monitor import PerformanceMonitor

logger = logging.getLogger(__name__)

class ProcessingPipeline:
    """
    Complete document processing pipeline with performance optimization
    Uses async processing and memory management for efficiency
    """
    
    def __init__(self, max_workers: int = 4):
        self.max_workers = max_workers
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.text_extractor = AdvancedTextExtractor()
        self.quality_checker = DocumentQualityChecker()
        self.performance_monitor = PerformanceMonitor()
        
        # Performance optimization settings
        self.chunk_size = 1024 * 1024  # 1MB chunks for large files
        self.memory_limit = 80  # 80% memory usage limit
        self.batch_size = 10    # Process documents in batches
        
    async def process_application_documents(self, application_id: int, 
                                          document_paths: List[str]) -> List[Dict[str, Any]]:
        """
        Process all documents for an application with performance optimization
        """
        logger.info(f"Starting processing pipeline for application {application_id}")
        start_time = time.time()
        
        # Monitor system resources
        initial_memory = psutil.virtual_memory().percent
        
        results = []
        
        # Process in batches for memory efficiency
        for i in range(0, len(document_paths), self.batch_size):
            batch = document_paths[i:i + self.batch_size]
            batch_results = await self._process_batch(application_id, batch)
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
        
        logger.info(f"Completed processing {len(document_paths)} documents in {total_time:.2f}s")
        
        return results
    
    async def _process_batch(self, application_id: int, document_paths: List[str]) -> List[Dict[str, Any]]:
        """Process a batch of documents concurrently"""
        tasks = []
        
        for doc_path in document_paths:
            task = self._process_single_document(application_id, doc_path)
            tasks.append(task)
        
        # Process concurrently but limit concurrency
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out exceptions
        valid_results = [r for r in results if not isinstance(r, Exception)]
        
        return valid_results
    
    async def _process_single_document(self, application_id: int, document_path: str) -> Dict[str, Any]:
        """Process a single document with full pipeline"""
        doc_start_time = time.time()
        
        try:
            # Step 1: Quality check
            quality_result = await self._check_document_quality(document_path)
            if not quality_result['is_valid']:
                return {
                    'document_path': document_path,
                    'status': 'rejected',
                    'error': quality_result['error'],
                    'processing_time': time.time() - doc_start_time
                }
            
            # Step 2: Extract text with performance monitoring
            extraction_result = await self._extract_text_async(document_path)
            
            # Step 3: Validate extraction quality
            if extraction_result['confidence_score'] < 0.5:
                extraction_result['warnings'].append("Low confidence extraction")
            
            # Add timing information
            extraction_result.update({
                'document_path': document_path,
                'processing_time': time.time() - doc_start_time,
                'status': 'completed',
                'quality_score': quality_result['quality_score']
            })
            
            return extraction_result
            
        except Exception as e:
            logger.error(f"Error processing document {document_path}: {e}")
            return {
                'document_path': document_path,
                'status': 'error',
                'error': str(e),
                'processing_time': time.time() - doc_start_time
            }
    
    async def _check_document_quality(self, document_path: str) -> Dict[str, Any]:
        """Check document quality asynchronously"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self.executor, 
            self.quality_checker.validate_document,
            document_path
        )
    
    async def _extract_text_async(self, document_path: str) -> Dict[str, Any]:
        """Extract text asynchronously with performance monitoring"""
        loop = asyncio.get_event_loop()
        
        # Use aiofiles for async file reading (better for large files)
        async with aiofiles.open(document_path, 'rb') as file:
            file_content = await file.read()
        
        # Process in executor to avoid blocking
        return await loop.run_in_executor(
            self.executor,
            self.text_extractor.extract_from_bytes,
            file_content,
            Path(document_path).suffix.lower()
        )
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get comprehensive performance metrics"""
        metrics = self.performance_monitor.get_metrics()
        
        # Add system-level metrics
        cpu_percent = psutil.cpu_percent(interval=1)
        memory_info = psutil.virtual_memory()
        disk_io = psutil.disk_io_counters()
        
        metrics.update({
            'system_performance': {
                'cpu_usage': cpu_percent,
                'memory_usage': memory_info.percent,
                'available_memory_gb': memory_info.available / (1024**3),
                'disk_read_mb': disk_io.read_bytes / (1024**2),
                'disk_write_mb': disk_io.write_bytes / (1024**2)
            },
            'optimization_settings': {
                'max_workers': self.max_workers,
                'chunk_size': self.chunk_size,
                'batch_size': self.batch_size,
                'memory_limit': self.memory_limit
            }
        })
        
        return metrics
    
    def optimize_performance(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Auto-optimize based on performance metrics"""
        recommendations = {}
        
        # Optimize worker count based on CPU usage
        if metrics['system_performance']['cpu_usage'] > 80:
            recommendations['reduce_workers'] = max(1, self.max_workers - 1)
        elif metrics['system_performance']['cpu_usage'] < 30:
            recommendations['increase_workers'] = min(8, self.max_workers + 1)
        
        # Optimize batch size based on memory usage
        if metrics['system_performance']['memory_usage'] > self.memory_limit:
            recommendations['reduce_batch_size'] = max(5, self.batch_size - 2)
        
        # Optimize chunk size based on processing time
        avg_time_per_doc = metrics.get('avg_processing_time_per_document', 0)
        if avg_time_per_doc > 5:  # If taking too long per document
            recommendations['reduce_chunk_size'] = max(512*1024, self.chunk_size // 2)
        
        return recommendations