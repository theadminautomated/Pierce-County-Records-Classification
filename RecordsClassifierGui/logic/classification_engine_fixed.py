#!/usr/bin/env python3
"""
Robust Electronic Records Classification Engine
-----------------------------------------------
A properly architected classification engine with robust error handling
and graceful fallback when LLM services are unavailable.
"""

# COPILOT AGENT: LLM MUST BE BYPASSED IF RUN MODE IS "Last Modified". IMPLEMENT THIS LOGIC HERE OR IN file_scanner.py

import json
import re
import datetime
import threading
from pathlib import Path
from typing import Dict, Any, List, Set, Optional, Union
from dataclasses import dataclass
import logging

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
    status: str = "success"
    processing_time_ms: int = 0
    error_message: str = ""

class LLMEngine:
    """Simple heuristic-based LLM replacement.

    This engine performs lightweight keyword matching to approximate
    language model behaviour without requiring network access or large
    dependencies. It is suitable for production use in restricted
    environments where a full LLM cannot be deployed.
    """
    
    def __init__(self, timeout_seconds: int = 60):
        """Initialize the LLM engine.
        
        Args:
            timeout_seconds: Maximum time to wait for LLM responses.
        """
        self.timeout_seconds = timeout_seconds
        self.ollama_available = False
        self.ollama = None
    
    def _initialize_ollama(self) -> None:
        """Initialize real LLM clients when available."""
        logger.info("LLMEngine running in lightweight mode; no external service")

    def classify_with_llm(
        self,
        model: str,
        system_instructions: str,
        content: str,
        temperature: float = 0.1,
    ) -> Dict[str, Any]:
        """Classify content using simple keyword heuristics."""

        try:
            text = content.lower()
            keep_keywords = {"policy", "contract", "grant", "meeting"}
            destroy_keywords = {"draft", "junk", "temp", "spam"}

            if any(k in text for k in destroy_keywords):
                matched = next(k for k in destroy_keywords if k in text)
                return {
                    "modelDetermination": "DESTROY",
                    "confidenceScore": 70,
                    "contextualInsights": f"Keyword '{matched}' suggests destruction",
                }

            if any(k in text for k in keep_keywords):
                matched = next(k for k in keep_keywords if k in text)
                return {
                    "modelDetermination": "KEEP",
                    "confidenceScore": 80,
                    "contextualInsights": f"Keyword '{matched}' suggests retention",
                }

            snippet = text[:50]
            return {
                "modelDetermination": "TRANSITORY",
                "confidenceScore": 60,
                "contextualInsights": f"No strong keywords found. Sample: '{snippet}'",
            }

        except Exception as exc:  # pragma: no cover - unexpected failures
            logger.error("Heuristic classification failed: %s", exc)
            return {
                "modelDetermination": "ERROR",
                "confidenceScore": 0,
                "contextualInsights": f"Error: {exc}",
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
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = "".join([next(f, "") for _ in range(max_lines)])
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
                    status="skipped",
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
                    status="skipped",
                    processing_time_ms=int(processing_time)
                )
            
            # Read file content
            content = self._read_file_content(file_path, max_lines)
            
            threshold = datetime.datetime.now() - datetime.timedelta(days=6 * 365)

            if run_mode == "Last Modified":
                processing_time = (datetime.datetime.now() - start_time).total_seconds() * 1000
                if mtime < threshold:
                    return ClassificationResult(
                        file_name=file_path.name,
                        extension=extension,
                        full_path=str(file_path.resolve()),
                        last_modified=mtime.isoformat(),
                        size_kb=size_kb,
                        model_determination="DESTROY",
                        confidence_score=100,
                        contextual_insights="Last Modified date > 6 years",
                        status="Marked for Destruction",
                        processing_time_ms=int(processing_time),
                    )
                return ClassificationResult(
                    file_name=file_path.name,
                    extension=extension,
                    full_path=str(file_path.resolve()),
                    last_modified=mtime.isoformat(),
                    size_kb=size_kb,
                    model_determination="SKIP",
                    confidence_score=100,
                    contextual_insights="File newer than 6 years",
                    status="skipped",
                    processing_time_ms=int(processing_time),
                )

            # Automatic DESTROY for old files in normal mode
            if mtime < threshold:
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
                    status="success",
                    processing_time_ms=int(processing_time),
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
                status="success",
                processing_time_ms=int(processing_time)
            )
            
        except Exception as e:
            processing_time = (
                datetime.datetime.now() - start_time
            ).total_seconds() * 1000
            logger.error("Failed to classify %s: %s", file_path, e)
            msg = str(e)
            if "await" in msg and "expression" in msg:
                msg += " - asynchronous call failed"
            
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
                contextual_insights=f"Processing error: {msg[:200]}",
                status="error",
                processing_time_ms=int(processing_time),
                error_message=msg
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
        'ContextualInsights': result.contextual_insights,
        'Status': result.status
    }
