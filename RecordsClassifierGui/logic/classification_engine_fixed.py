#!/usr/bin/env python3
"""
Robust Electronic Records Classification Engine
-----------------------------------------------
A properly architected classification engine with robust error handling
and graceful fallback when LLM services are unavailable.
"""

# COPILOT AGENT: LLM MUST BE BYPASSED IF RUN MODE IS "Last Modified". IMPLEMENT THIS LOGIC HERE OR IN file_scanner.py

import os
import sys
import json
import re
import datetime
import threading
from pathlib import Path
from typing import Dict, Any, List, Set, Optional, Union
from dataclasses import dataclass
import logging
import concurrent.futures

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# File type constants - sync with file_scanner.py
INCLUDE_EXT: Set[str] = frozenset({
    '.txt', '.csv', '.docx', '.xlsx', '.pptx', '.pdf', '.html', '.htm', '.md',
    '.rtf', '.odt', '.xml', '.json', '.yaml', '.yml', '.log', '.tsv'
})

EXCLUDE_EXT: Set[str] = frozenset({
    '.tmp', '.bak', '.old', '.zip', '.rar', '.tar', '.gz', '.7z',
    '.exe', '.dll', '.sys', '.iso', '.dmg', '.apk', '.msi', '.ps1', '.psd1',
    '.psm1', '.db', '.mdb', '.accdb', '.sqlite', '.dbf', '.log', '.swp', '.swo'
})

@dataclass
class ClassificationResult:
    """Structured result from file classification."""
    file_name: str
    extension: str
    full_path: str
    last_modified: str
    size_kb: float
    model_determination: str
    confidence_score: int
    contextual_insights: str
    processing_time_ms: int = 0
    error_message: str = ""

class LLMEngine:
    """Handles LLM interactions with proper timeout and error handling.
    
    This class manages communication with Ollama LLM services, providing
    robust error handling, timeout protection, and graceful fallback when
    services are unavailable.
    """
    
    def __init__(self, timeout_seconds: int = 60):
        """Initialize the LLM engine.
        
        Args:
            timeout_seconds: Maximum time to wait for LLM responses.
        """
        self.timeout_seconds = timeout_seconds
        self.ollama_available = False
        self._initialize_ollama()
    
    def _initialize_ollama(self):
        """Initialize ollama with timeout protection using threading.
        
        Uses threading-based timeout for Windows compatibility instead of
        signal-based timeouts which don't work on Windows.
        """
        try:
            # Use threading-based timeout for Windows compatibility
            ollama_result = {'ollama': None, 'available': False, 'error': None}
            
            def load_ollama():
                try:
                    import ollama
                    ollama_result['ollama'] = ollama
                    # Test if ollama service is actually running
                    models = ollama.list()
                    ollama_result['available'] = True
                    logger.info("Ollama service is available")
                except Exception as e:
                    ollama_result['error'] = e
                    logger.warning(f"Ollama import succeeded but service unavailable: {e}")
            
            # Start the import in a thread with timeout
            thread = threading.Thread(target=load_ollama)
            thread.daemon = True
            thread.start()
            thread.join(timeout=10)  # 10-second timeout
            
            if thread.is_alive():
                logger.warning("Ollama initialization timed out")
                self.ollama = None
                self.ollama_available = False
            elif ollama_result['error']:
                logger.warning(f"Ollama not available: {ollama_result['error']}")
                self.ollama = None
                self.ollama_available = False
            else:
                self.ollama = ollama_result['ollama']
                self.ollama_available = ollama_result['available']
                
        except Exception as e:
            logger.warning(f"Ollama initialization failed: {e}")
            self.ollama = None
            self.ollama_available = False
    def classify_with_llm(
        self,
        model: str,
        system_instructions: str,
        content: str,
        temperature: float = 0.1
    ) -> Dict[str, Any]:
        """Classify content using LLM with robust error handling.
        
        Args:
            model: Name of the LLM model to use.
            system_instructions: System prompt for the LLM.
            content: File content to classify.
            temperature: LLM temperature setting (0.0-1.0).
            
        Returns:
            Dictionary containing classification results with keys:
            - modelDetermination: Classification result (TRANSITORY/DESTROY/KEEP)
            - confidenceScore: Confidence score (1-100)
            - contextualInsights: Explanation of the classification
        """
        
        if not self.ollama_available or not self.ollama:
            return {
                "modelDetermination": "ERROR",
                "confidenceScore": 0,
                "contextualInsights": "LLM service unavailable"
            }
        
        generation_config = {
            "temperature": max(0.0, min(1.0, temperature)),
            "top_p": 0.9,
            "top_k": 40,
            "num_ctx": 8192,
            "repeat_penalty": 1.2,
            "stop": ["<end_of_turn>", "```", "\n\n"],
            "system": system_instructions
        }
        
        prompt = f"Classify this content per instructions:\n{content[:5000]}\nOutput JSON only:"
        
        try:
            # Use thread-based timeout for Windows compatibility
            result_container = {'result': None, 'error': None}
            
            def llm_call():
                try:
                    response = self.ollama.chat(
                        model=model,
                        messages=[
                            {"role": "system", "content": system_instructions or ""},
                            {"role": "user", "content": prompt}
                        ],
                        options=generation_config,
                        stream=False
                    )
                    result_container['result'] = response
                except Exception as e:
                    result_container['error'] = e
            
            # Start LLM call in thread with timeout
            thread = threading.Thread(target=llm_call)
            thread.daemon = True
            thread.start()
            thread.join(timeout=self.timeout_seconds)
            
            if thread.is_alive():
                logger.error("LLM call timed out")
                return {
                    "modelDetermination": "ERROR",
                    "confidenceScore": 0,
                    "contextualInsights": f"LLM call timed out after {self.timeout_seconds} seconds"
                }
            
            if result_container['error']:
                raise result_container['error']
            
            response = result_container['result']
            raw = response.get('message', {}).get('content', '') if isinstance(response, dict) else str(response)
            
            # Extract JSON from response
            json_match = re.search(r'\{[^{}]*\}', raw, re.DOTALL)
            if not json_match:
                raise ValueError(f'No valid JSON found in response: {raw[:200]}')
            
            try:
                result = json.loads(json_match.group(0))
            except json.JSONDecodeError as e:
                raise ValueError(f'JSON decode error: {e}\nExtracted: {json_match.group(0)[:200]}')
            
            # Validate required fields
            validation_rules = {
                'modelDetermination': (
                    lambda x: x in ("TRANSITORY", "DESTROY", "KEEP"),
                    "must be TRANSITORY, DESTROY, or KEEP"
                ),
                'confidenceScore': (
                    lambda x: isinstance(x, (int, float)) and 1 <= x <= 100,
                    "must be number 1-100"
                ),
                'contextualInsights': (
                    lambda x: isinstance(x, str),
                    "must be string"
                )
            }
            
            for key, (validator, msg) in validation_rules.items():
                if key not in result:
                    raise ValueError(f'Missing required key: {key}')
                if not validator(result[key]):
                    raise ValueError(f'Invalid {key}: {result[key]} ({msg})')
            
            return result
            
        except Exception as e:
            logger.error(f"LLM classification failed: {e}")
            return {
                "modelDetermination": "ERROR",
                "confidenceScore": 0,
                "contextualInsights": f"Classification error: {str(e)[:200]}"
            }

class ClassificationEngine:
    """Main classification engine with hybrid scoring.
    
    Combines LLM-based classification with rule-based logic for optimal
    accuracy. Automatically destroys files older than 6 years and applies
    confidence adjustments based on file characteristics.
    """
    
    def __init__(self, timeout_seconds: int = 60):
        """Initialize the classification engine.
        
        Args:
            timeout_seconds: Maximum time to wait for LLM responses.
        """
        self.llm_engine = LLMEngine(timeout_seconds)
    def _hybrid_confidence(
        self, 
        llm_score: int, 
        file_path: Path, 
        content: str, 
        determination: str
    ) -> int:
        """Calculate hybrid confidence score combining LLM and rule-based logic.
        
        Args:
            llm_score: Confidence score from LLM (1-100).
            file_path: Path to the file being classified.
            content: File content that was classified.
            determination: Classification result from LLM.
            
        Returns:
            Adjusted confidence score (1-100) based on hybrid logic:
            - DESTROY for >6 years old: always 100
            - Empty files: always 0
            - DESTROY for newer files: capped at 80
            - Other classifications: use LLM score with bounds checking
        """
        try:
            if determination == "DESTROY":
                mtime = datetime.datetime.fromtimestamp(file_path.stat().st_mtime)
                threshold = datetime.datetime.now() - datetime.timedelta(days=6 * 365)
                if mtime < threshold:
                    return 100
                else:
                    return min(80, max(1, int(llm_score)))
            elif not content.strip():
                return 0
            else:
                return min(100, max(1, int(llm_score)))
        except Exception:
            return min(100, max(1, int(llm_score)))
    
    def _read_file_content(self, file_path: Path, max_lines: int = 100) -> str:
        """Safely read file content with proper error handling."""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = ''.join([next(f, '') for _ in range(max_lines)])
            return content
        except Exception as e:
            logger.warning(f"Could not read file {file_path}: {e}")
            return ''
    
    def classify_file(
        self,
        file_path: Union[str, Path],
        model: str = 'llama2',
        instructions: str = '',
        temperature: float = 0.1,
        max_lines: int = 100,
        run_mode: str = 'Classification'
    ) -> ClassificationResult:
        """
        Classify a single file with comprehensive error handling.
        
        Args:
            file_path: Path to the file to classify
            model: LLM model name
            instructions: System instructions for classification
            temperature: LLM temperature
            max_lines: Maximum lines to read from file
            run_mode: Classification mode ('Classification' or 'Last Modified')
            
        Returns:
            ClassificationResult with all metadata and classification
        """
        start_time = datetime.datetime.now()
        file_path = Path(file_path)
        
        try:
            # Get file metadata
            stat_info = file_path.stat()
            mtime = datetime.datetime.fromtimestamp(stat_info.st_mtime)
            size_kb = round(stat_info.st_size / 1024, 2)
            
            # Check for excluded file extensions
            extension = file_path.suffix.lower()
            if extension in EXCLUDE_EXT:
                processing_time = (datetime.datetime.now() - start_time).total_seconds() * 1000
                return ClassificationResult(
                    file_name=file_path.name,
                    extension=extension,
                    full_path=str(file_path.resolve()),
                    last_modified=mtime.isoformat(),
                    size_kb=size_kb,
                    model_determination="SKIP",
                    confidence_score=100,
                    contextual_insights=f"Excluded file type: {extension}",
                    processing_time_ms=int(processing_time)
                )
            
            # Check if file extension is not in include list
            if extension not in INCLUDE_EXT:
                processing_time = (datetime.datetime.now() - start_time).total_seconds() * 1000
                return ClassificationResult(
                    file_name=file_path.name,
                    extension=extension,
                    full_path=str(file_path.resolve()),
                    last_modified=mtime.isoformat(),
                    size_kb=size_kb,
                    model_determination="SKIP",
                    confidence_score=100,
                    contextual_insights=f"Unsupported file type: {extension}",
                    processing_time_ms=int(processing_time)
                )
            
            # Read file content
            content = self._read_file_content(file_path, max_lines)
            
            # Check if file is old enough for automatic DESTROY classification
            # THIS LOGIC NEEDS TO BE THE CORE LOGIC FOR THE LASTMODIFIED MODE
            threshold = datetime.datetime.now() - datetime.timedelta(days=6 * 365)
            if mtime < threshold:
                # Automatic DESTROY for old files
                processing_time = (datetime.datetime.now() - start_time).total_seconds() * 1000
                return ClassificationResult(
                    file_name=file_path.name,
                    extension=file_path.suffix,
                    full_path=str(file_path.resolve()),
                    last_modified=mtime.isoformat(),
                    size_kb=size_kb,
                    model_determination="DESTROY",
                    confidence_score=100,
                    contextual_insights="Older than 6 years - automatic destroy",
                    processing_time_ms=int(processing_time)
                )
            
            # Use Last Modified mode classification or LLM
            if run_mode == "Last Modified":
                # Skip LLM for Last Modified mode - classify as TRANSITORY by default
                processing_time = (datetime.datetime.now() - start_time).total_seconds() * 1000
                return ClassificationResult(
                    file_name=file_path.name,
                    extension=extension,
                    full_path=str(file_path.resolve()),
                    last_modified=mtime.isoformat(),
                    size_kb=size_kb,
                    model_determination="TRANSITORY",
                    confidence_score=75,
                    contextual_insights="Based on last modified date - less than 6 years old",
                    processing_time_ms=int(processing_time)
                )
            
            # Use LLM for classification
            llm_result = self.llm_engine.classify_with_llm(
                model=model,
                system_instructions=instructions,
                content=content,
                temperature=temperature
            )
            
            # Apply hybrid confidence scoring
            confidence_score = self._hybrid_confidence(
                llm_result.get('confidenceScore', 0),
                file_path,
                content,
                llm_result.get('modelDetermination', 'ERROR')
            )
            
            processing_time = (datetime.datetime.now() - start_time).total_seconds() * 1000
            
            return ClassificationResult(
                file_name=file_path.name,
                extension=file_path.suffix,
                full_path=str(file_path.resolve()),
                last_modified=mtime.isoformat(),
                size_kb=size_kb,
                model_determination=llm_result.get('modelDetermination', 'ERROR'),
                confidence_score=confidence_score,
                contextual_insights=llm_result.get('contextualInsights', ''),
                processing_time_ms=int(processing_time)
            )
            
        except Exception as e:
            processing_time = (datetime.datetime.now() - start_time).total_seconds() * 1000
            logger.error(f"Failed to classify {file_path}: {e}")
            
            # Return error result with as much metadata as possible
            try:
                stat_info = file_path.stat()
                mtime = datetime.datetime.fromtimestamp(stat_info.st_mtime)
                size_kb = round(stat_info.st_size / 1024, 2)
            except:
                mtime = datetime.datetime.now()
                size_kb = 0
            
            return ClassificationResult(
                file_name=file_path.name,
                extension=file_path.suffix,
                full_path=str(file_path.resolve()),
                last_modified=mtime.isoformat(),
                size_kb=size_kb,
                model_determination="ERROR",
                confidence_score=0,
                contextual_insights=f"Processing error: {str(e)[:200]}",
                processing_time_ms=int(processing_time),
                error_message=str(e)
            )

# Create a global instance for backward compatibility
_classification_engine = ClassificationEngine()

def process_file(
    file_path: Path,
    model: str,
    instructions: str,
    temperature: float,
    lines: int,
    run_mode: str = 'Classification'
) -> Dict[str, Any]:
    """
    Legacy compatibility function that matches the original interface.
    
    Args:
        file_path: Path to the file to classify
        model: LLM model name
        instructions: System instructions for classification
        temperature: LLM temperature
        lines: Maximum lines to read from file
        run_mode: Classification mode ('Classification' or 'Last Modified')
    
    Returns:
        Dictionary with classification results in the original format
    """
    result = _classification_engine.classify_file(
        file_path=file_path,
        model=model,
        instructions=instructions,
        temperature=temperature,
        max_lines=lines,
        run_mode=run_mode
    )
    
    # Convert to original format
    return {
        'FileName': result.file_name,
        'Extension': result.extension,
        'FullPath': result.full_path,
        'LastModified': result.last_modified,
        'SizeKB': result.size_kb,
        'ModelDetermination': result.model_determination,
        'ConfidenceScore': result.confidence_score,
        'ContextualInsights': result.contextual_insights
    }
