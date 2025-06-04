"""
Test harness for Pierce County Records Classifier validation pipeline.
Runs end-to-end classification and validation on sample data.
"""
from core.llm_engine import classify_with_model
import json

def run_test():
    sample_content = "This is a temporary memo for routine use."
    result = classify_with_model(sample_content)
    print("Classification result:")
    print(json.dumps(result, indent=2))
    if 'validation_error' in result:
        print("\nVALIDATION ERROR:")
        print(result['validation_error'])
    else:
        print("\nValidation PASSED.")

if __name__ == "__main__":
    run_test()
