# """
# Big O Notation Analysis for Phase 1 Performance
# Comprehensive performance analysis and optimization
# """
# import time
# import psutil
# import matplotlib.pyplot as plt
# import numpy as np
# from typing import List, Dict, Any
# import json

# class BigOAnalyzer:
#     """
#     Analyzes algorithm complexity and performance characteristics
#     """
    
#     def __init__(self):
#         self.results = {}
    
#     def analyze_document_processing_complexity(self, document_sizes: List[int], 
#                                              processing_times: List[float]) -> Dict[str, Any]:
#         """
#         Analyze document processing algorithm complexity
#         """
#         analysis = {
#             'input_sizes': document_sizes,
#             'processing_times': processing_times,
#             'complexity_analysis': {}
#         }
        
#         # Calculate different complexity fits
#         if len(document_sizes) >= 3:
#             # Linear fit: O(n)
#             linear_fit = np.polyfit(document_sizes, processing_times, 1)
#             linear_pred = np.polyval(linear_fit, document_sizes)
#             linear_error = np.mean((processing_times - linear_pred) ** 2)
            
#             # Quadratic fit: O(n²)
#             quadratic_fit = np.polyfit(document_sizes, processing_times, 2)
#             quadratic_pred = np.polyval(quadratic_fit, document_sizes)
#             quadratic_error = np.mean((processing_times - quadratic_pred) ** 2)
            
#             # Log-linear fit: O(n log n)
#             log_sizes = np.log(document_sizes)
#             log_linear_fit = np.polyfit(log_sizes, processing_times, 1)
#             log_linear_pred = np.polyval(log_linear_fit, log_sizes)
#             log_linear_error = np.mean((processing_times - log_linear_pred) ** 2)
            
#             # Determine best fit
#             errors = {
#                 'O(n)': linear_error,
#                 'O(n²)': quadratic_error,
#                 'O(n log n)': log_linear_error
#             }
            
#             best_complexity = min(errors, key=errors.get)
            
#             analysis['complexity_analysis'] = {
#                 'best_fit': best_complexity,
#                 'fit_errors': errors,
#                 'linear_coefficients': linear_fit.tolist(),
#                 'quadratic_coefficients': quadratic_fit.tolist(),
#                 'log_linear_coefficients': log_linear_fit.tolist()
#             }
        
#         return analysis
    
#     def analyze_memory_complexity(self, input_sizes: List[int], 
#                                 memory_usage: List[float]) -> Dict[str, Any]:
#         """
#         Analyze memory usage complexity
#         """
#         analysis = {
#             'input_sizes': input_sizes,
#             'memory_usage': memory_usage,
#             'memory_analysis': {}
#         }
        
#         if len(input_sizes) >= 3:
#             # Linear memory: O(n)
#             linear_fit = np.polyfit(input_sizes, memory_usage, 1)
#             linear_pred = np.polyval(linear_fit, input_sizes)
#             linear_r2 = 1 - (np.sum((memory_usage - linear_pred) ** 2) / np.sum((memory_usage - np.mean(memory_usage)) ** 2))
            
#             # Constant memory: O(1)
#             constant_pred = np.full_like(input_sizes, np.mean(memory_usage))
#             constant_r2 = 1 - (np.sum((memory_usage - constant_pred) ** 2) / np.sum((memory_usage - np.mean(memory_usage)) ** 2))
            
#             analysis['memory_analysis'] = {
#                 'linear_memory_r2': linear_r2,
#                 'constant_memory_r2': constant_r2,
#                 'memory_efficiency': 'O(n)' if linear_r2 > 0.8 else 'O(1)' if constant_r2 > 0.8 else 'Unknown',
#                 'linear_coefficients': linear_fit.tolist()
#             }
        
#         return analysis
    
#     def generate_performance_report(self, test_results: Dict[str, Any]) -> str:
#         """
#         Generate comprehensive performance report
#         """
#         report = f"""
# # Phase 1 Performance Analysis Report

# Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}

# ## Executive Summary

# ### Document Processing Performance
# - **Best Complexity**: {test_results.get('document_processing', {}).get('complexity_analysis', {}).get('best_fit', 'Unknown')}
# - **Average Processing Time**: {np.mean(test_results.get('document_processing', {}).get('processing_times', [])):.3f} seconds
# - **Memory Efficiency**: {test_results.get('memory_usage', {}).get('memory_analysis', {}).get('memory_efficiency', 'Unknown')}

# ### System Resource Usage
# - **Peak Memory Usage**: {max(test_results.get('memory_usage', {}).get('memory_usage', [])):.1f} MB
# - **Average CPU Usage**: {np.mean(test_results.get('cpu_usage', [])):.1f}%
# - **Total Processing Time**: {sum(test_results.get('document_processing', {}).get('processing_times', [])):.3f} seconds

# ## Detailed Analysis

# ### Algorithm Complexity Analysis