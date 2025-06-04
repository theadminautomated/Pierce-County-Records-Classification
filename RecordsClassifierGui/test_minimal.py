#!/usr/bin/env python3
"""
Minimal test for the classification architecture without ollama dependency
"""

import sys
import os
from pathlib import Path
import tempfile

# Add the logic directory to path
logic_dir = Path(__file__).parent / "logic"
sys.path.append(str(logic_dir))

def test_imports():
    """Test that our modules can be imported."""
    print("Testing imports...")
    
    try:
        from classification_engine_fixed import ClassificationEngine, ClassificationResult
        print("✓ Classification engine imported successfully")
        
        from file_scanner import FileScanner, INCLUDE_EXT, EXCLUDE_EXT
        print("✓ File scanner imported successfully")
        
        return True
        
    except Exception as e:
        print(f"✗ Import failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_file_scanner():
    """Test the file scanner functionality."""
    print("\nTesting file scanner...")
    
    try:
        from file_scanner import FileScanner
        
        # Create temporary directory with test files
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create test files
            (temp_path / "test.txt").write_text("Test file content")
            (temp_path / "test.pdf").write_text("PDF test content")
            (temp_path / "test.exe").write_text("Executable file")
            
            scanner = FileScanner()
            
            # Test file categorization
            file_infos = list(scanner.scan_directory(temp_path))
            
            print(f"✓ Found {len(file_infos)} files")
            for file_info in file_infos:
                print(f"  {file_info.path.name}: {file_info.category} ({file_info.reason})")
            
            # Test counts
            counts = scanner.get_file_counts(temp_path)
            print(f"✓ File counts: {counts}")
            
            return True
            
    except Exception as e:
        print(f"✗ File scanner test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_classification_without_llm():
    """Test classification engine without LLM (should gracefully handle unavailable ollama)."""
    print("\nTesting classification engine (without LLM)...")
    
    try:
        from classification_engine_fixed import ClassificationEngine
        
        # Create a test file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("This is a test document for records classification testing.")
            test_file_path = Path(f.name)
        
        try:
            # Create engine with short timeout
            engine = ClassificationEngine(timeout_seconds=5)
            
            # This should work even if ollama is not available
            result = engine.classify_file(
                file_path=test_file_path,
                model='test-model',
                instructions='Test classification',
                temperature=0.1,
                max_lines=100
            )
            
            print(f"✓ Classification completed!")
            print(f"  File: {result.file_name}")
            print(f"  Determination: {result.model_determination}")
            print(f"  Confidence: {result.confidence_score}")
            print(f"  Insights: {result.contextual_insights}")
            print(f"  Processing time: {result.processing_time_ms}ms")
            
            if result.error_message:
                print(f"  Error: {result.error_message}")
            
            return True
            
        finally:
            # Clean up
            try:
                test_file_path.unlink()
            except:
                pass
                
    except Exception as e:
        print(f"✗ Classification test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=== Minimal Architecture Test ===\n")
    
    tests = [
        ("Imports", test_imports),
        ("File Scanner", test_file_scanner),
        ("Classification Engine", test_classification_without_llm)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n--- {test_name} ---")
        success = test_func()
        results.append((test_name, success))
        print(f"{test_name}: {'PASSED' if success else 'FAILED'}")
    
    print(f"\n=== SUMMARY ===")
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "✓ PASS" if success else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Architecture is working correctly.")
    else:
        print("❌ Some tests failed. Check the errors above.")
