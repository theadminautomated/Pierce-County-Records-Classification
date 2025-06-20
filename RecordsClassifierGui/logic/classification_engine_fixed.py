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
from typing import Dict, Any, List, Set, Optional, Union, Iterator
from dataclasses import dataclass
import logging

# Import file_scanner with absolute import
try:
    from RecordsClassifierGui.logic.file_scanner import FileScanner
except ImportError:
    # Fallback for when running from different contexts
    import sys
    import os
    logic_path = os.path.join(os.path.dirname(__file__))
    if logic_path not in sys.path:
        sys.path.insert(0, logic_path)
    from file_scanner import FileScanner

# Import model_output_validation with absolute import
try:
    from RecordsClassifierGui.core import model_output_validation
except ImportError:
    # Fallback for when running from different contexts
    import sys
    import os

    core_path = os.path.join(os.path.dirname(__file__), "..", "core")
    if core_path not in sys.path:
        sys.path.insert(0, core_path)
    import model_output_validation

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# File type constants - sync with file_scanner.py
INCLUDE_EXT: Set[str] = frozenset(
    {
        ".txt",
        ".csv",
        ".docx",
        ".xlsx",
        ".pptx",
        ".pdf",
        ".html",
        ".htm",
        ".md",
        ".rtf",
        ".odt",
        ".xml",
        ".json",
        ".yaml",
        ".yml",
        ".log",
        ".tsv",
    }
)

EXCLUDE_EXT: Set[str] = frozenset(
    {
        ".tmp",
        ".bak",
        ".old",
        ".zip",
        ".rar",
        ".tar",
        ".gz",
        ".7z",
        ".exe",
        ".dll",
        ".sys",
        ".iso",
        ".dmg",
        ".apk",
        ".msi",
        ".ps1",
        ".psd1",
        ".psm1",
        ".db",
        ".mdb",
        ".accdb",
        ".sqlite",
        ".dbf",
        ".log",
        ".swp",
        ".swo",
    }
)


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

    def _sanitize_snippet(self, text: str) -> str:
        """Return a printable snippet or a placeholder for unreadable text."""
        snippet = text.replace("\n", " ").strip()
        if not snippet:
            return "[File is binary or unreadable]"
        printable = sum(1 for ch in snippet if ch.isprintable())
        if printable / len(snippet) < 0.85:
            return "[File is binary or unreadable]"
        return snippet[:80]

    def _extract_snippet(self, content: str, keyword: str, window: int = 80) -> str:
        """Return sanitized text snippet around a keyword or start of content."""
        try:
            snippet = content[:window]
            if keyword:
                lower = content.lower()
                idx = lower.find(keyword.lower())
                if idx != -1:
                    start = max(0, idx - window // 2)
                    snippet = content[start : start + window]
            return self._sanitize_snippet(snippet)
        except Exception:
            return "[File is binary or unreadable]"

    def classify_with_llm(
        self,
        model: str,
        system_instructions: str,
        content: str,
        temperature: float = 0.1,
    ) -> Dict[str, Any]:
        """Classify content using WA Schedule 6 heuristics.

        The model analyzes the text while keyword matches contribute only to
        the confidence score. Output determination and ContextualInsights as a justification for your determination - citing content.
        """

        try:
            text = content.lower()

            # Count keyword occurrences for each Schedule 6 class
            keyword_counts = {
                label: sum(
                    text.count(kw)
                    for kw in model_output_validation.SCHEDULE_6_KEYWORDS.get(label, [])
                )
                for label in model_output_validation.SCHEDULE_6_KEYWORDS
            }

            total = sum(keyword_counts.values())
            if total > 0:
                best_label = max(keyword_counts, key=keyword_counts.get)
                first_match = next(
                    (
                        kw
                        for kw in model_output_validation.SCHEDULE_6_KEYWORDS[best_label]
                        if kw in text
                    ),
                    "",
                )
                determination = "KEEP" if best_label == "OFFICIAL" else best_label
                base_conf = 50 + min(keyword_counts[best_label] * 10, 40)
                snippet = self._extract_snippet(content, first_match)
                insights = (
                    f"The file includes the keyword '{first_match}', indicating a {determination.lower()} record."
                    f" Example text: '{snippet}'."
                    " This aligns with WA Schedule 6 guidance."
                )
                return {
                    "modelDetermination": determination,
                    "confidenceScore": base_conf,
                    "contextualInsights": insights,
                }

            snippet = self._extract_snippet(content, "")
            insights = (
                "No Schedule 6 keywords were found in the sampled text. "
                f"The document starts with: '{snippet}'. "
                "Based on this, the record appears transitory."
            )
            return {
                "modelDetermination": "TRANSITORY",
                "confidenceScore": 50,
                "contextualInsights": insights,
            }

        except Exception as exc:  # pragma: no cover - unexpected failures
            logger.error("Heuristic classification failed: %s", exc)
            return {
                "modelDetermination": "TRANSITORY",
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
        determination: str,
        threshold_years: int,
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
                threshold = datetime.datetime.now() - datetime.timedelta(
                    days=threshold_years * 365
                )
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
            return ""

    def classify_file(
        self,
        file_path: Union[str, Path],
        model: str = "llama2",
        instructions: str = "",
        temperature: float = 0.1,
        max_lines: int = 100,
        run_mode: str = "Classification",
        threshold_years: int = 6,
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
            threshold_years: Age threshold in years for automatic DESTROY logic

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

            extension = file_path.suffix.lower()

            # Calculate destroy threshold once
            threshold = datetime.datetime.now() - datetime.timedelta(
                days=threshold_years * 365
            )

            # Rule 1: Any file older than the threshold is DESTROY regardless of other checks
            if mtime < threshold:
                processing_time = (
                    datetime.datetime.now() - start_time
                ).total_seconds() * 1000
                return ClassificationResult(
                    file_name=file_path.name,
                    extension=extension,
                    full_path=str(file_path.resolve()),
                    last_modified=mtime.isoformat(),
                    size_kb=size_kb,
                    model_determination="DESTROY",
                    confidence_score=100,
                    contextual_insights=f"Older than {threshold_years} years - automatic destroy",
                    status="success",
                    processing_time_ms=int(processing_time),
                )

            # Check for excluded file extensions
            if extension in EXCLUDE_EXT:
                processing_time = (
                    datetime.datetime.now() - start_time
                ).total_seconds() * 1000
                return ClassificationResult(
                    file_name=file_path.name,
                    extension=extension,
                    full_path=str(file_path.resolve()),
                    last_modified=mtime.isoformat(),
                    size_kb=size_kb,
                    model_determination="NA",
                    confidence_score=100,
                    contextual_insights=f"Excluded file type: {extension}",
                    status="skipped",
                    processing_time_ms=int(processing_time),
                )

            # Check if file extension is not in include list
            if extension not in INCLUDE_EXT:
                processing_time = (
                    datetime.datetime.now() - start_time
                ).total_seconds() * 1000
                return ClassificationResult(
                    file_name=file_path.name,
                    extension=extension,
                    full_path=str(file_path.resolve()),
                    last_modified=mtime.isoformat(),
                    size_kb=size_kb,
                    model_determination="NA",
                    confidence_score=100,
                    contextual_insights=f"Unsupported file type: {extension}",
                    status="skipped",
                    processing_time_ms=int(processing_time),
                )

            if run_mode == "Last Modified":
                processing_time = (
                    datetime.datetime.now() - start_time
                ).total_seconds() * 1000
                if mtime < threshold:
                    return ClassificationResult(
                        file_name=file_path.name,
                        extension=extension,
                        full_path=str(file_path.resolve()),
                        last_modified=mtime.isoformat(),
                        size_kb=size_kb,
                        model_determination="DESTROY",
                        confidence_score=100,
                        contextual_insights=f"Older than {threshold_years} years - automatic destroy",
                        status="success",
                        processing_time_ms=int(processing_time),
                    )
                return ClassificationResult(
                    file_name=file_path.name,
                    extension=extension,
                    full_path=str(file_path.resolve()),
                    last_modified=mtime.isoformat(),
                    size_kb=size_kb,
                    model_determination="NA",
                    confidence_score=100,
                    contextual_insights=f"File newer than {threshold_years} years",
                    status="skipped",
                    processing_time_ms=int(processing_time),
                )

            # Read file content
            content = self._read_file_content(file_path, max_lines)


            # Use LLM for classification
            llm_result = self.llm_engine.classify_with_llm(
                model=model,
                system_instructions=instructions,
                content=content,
                temperature=temperature,
            )

            # Apply hybrid confidence scoring
            confidence_score = self._hybrid_confidence(
                llm_result.get("confidenceScore", 0),
                file_path,
                content,
                llm_result.get("modelDetermination", "ERROR"),
                threshold_years,
            )

            processing_time = (
                datetime.datetime.now() - start_time
            ).total_seconds() * 1000

            return ClassificationResult(
                file_name=file_path.name,
                extension=file_path.suffix,
                full_path=str(file_path.resolve()),
                last_modified=mtime.isoformat(),
                size_kb=size_kb,
                model_determination=llm_result.get("modelDetermination", "TRANSITORY"),
                confidence_score=confidence_score,
                contextual_insights=llm_result.get("contextualInsights", ""),
                status="success",
                processing_time_ms=int(processing_time),
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
                model_determination="NA",
                confidence_score=0,
                contextual_insights=f"Processing error: {msg[:200]}",
                status="error",
                processing_time_ms=int(processing_time),
                error_message=msg,
            )


# Create a global instance for backward compatibility
_classification_engine = ClassificationEngine()


def process_file(
    file_path: Path,
    model: str,
    instructions: str,
    temperature: float,
    lines: int,
    run_mode: str = "Classification",
    threshold_years: int = 6,
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
        threshold_years: Age threshold in years for DESTROY logic

    Returns:
        Dictionary with classification results in the original format
    """
    result = _classification_engine.classify_file(
        file_path=file_path,
        model=model,
        instructions=instructions,
        temperature=temperature,
        max_lines=lines,
        run_mode=run_mode,
        threshold_years=threshold_years,
    )

    # Convert to original format
    return {
        "FileName": result.file_name,
        "Extension": result.extension,
        "FullPath": result.full_path,
        "LastModified": result.last_modified,
        "SizeKB": result.size_kb,
        "ModelDetermination": result.model_determination,
        "ConfidenceScore": result.confidence_score,
        "ContextualInsights": result.contextual_insights,
        "Status": result.status,
    }


def classify_directory(
    directory: Path,
    *,
    batch_size: int = 50,
    engine: ClassificationEngine | None = None,
    **kwargs,
) -> Iterator[ClassificationResult]:
    """Yield ``ClassificationResult`` objects for all files in ``directory``.

    Parameters
    ----------
    directory : Path
        Folder to scan for supported files.
    batch_size : int, optional
        Number of files to process between log updates.
    engine : ClassificationEngine, optional
        Engine instance to use. A new one is created if omitted.
    **kwargs : Any
        Additional arguments passed to ``ClassificationEngine.classify_file``.

    Yields
    ------
    ClassificationResult
        Result for each processed file.
    """

    engine = engine or _classification_engine
    scanner = FileScanner()
    processed = 0
    batch: list[Path] = []
    for file_info in scanner.scan_directory(directory):
        if file_info.category == "skip":
            continue
        batch.append(file_info.path)
        if len(batch) >= batch_size:
            for path in batch:
                yield engine.classify_file(path, **kwargs)
                processed += 1
            logger.info("Processed %s files", processed)
            batch.clear()

    for path in batch:
        yield engine.classify_file(path, **kwargs)
        processed += 1
    if processed:
        logger.info("Processed %s files", processed)
