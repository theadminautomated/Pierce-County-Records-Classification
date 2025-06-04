#!/usr/bin/env python3
"""
Test script for the fixed classification engine
"""

import sys
import os
from pathlib import Path

# Add the logic directory to path
logic_dir = Path(__file__).parent / "logic"
sys.path.append(str(logic_dir))

from classification_engine_fixed import ClassificationEngine
import tempfile

def test_classification():
    """Test the classification engine with a temporary file."""
    print("Testing Classification Engine...")
    
    # Initialize engine
    engine = ClassificationEngine(timeout_seconds=10)
    
    # Create a test file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write("This is a test document for Pierce County Records classification. "
                "It contains some sample text that should be classified properly.")
        test_file_path = Path(f.name)
    
    try:
        # Test classification
        result = engine.classify_file(
            file_path=test_file_path,
            model='llama2',
            instructions='Classify this document according to Pierce County Schedule 6 retention rules.',
            temperature=0.1,
            max_lines=100
        )
        
        print(f"✓ Classification completed successfully!")
        print(f"  File: {result.file_name}")
        print(f"  Determination: {result.model_determination}")
        print(f"  Confidence: {result.confidence_score}")
        print(f"  Insights: {result.contextual_insights}")
        print(f"  Processing time: {result.processing_time_ms}ms")
        
        if result.error_message:
            print(f"  Error: {result.error_message}")
        
        return True
        
    except Exception as e:
        print(f"✗ Classification failed: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        # Clean up
        try:
            test_file_path.unlink()
        except:
            pass

if __name__ == "__main__":
    success = test_classification()
    print(f"\nTest {'PASSED' if success else 'FAILED'}")
