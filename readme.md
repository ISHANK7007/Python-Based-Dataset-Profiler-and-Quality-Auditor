# Python-Based Dataset Profiler and Quality Auditor

## Project Objective
A Python-only tool that scans CSV datasets, analyzes structure and statistical properties, detects quality issues (e.g., nulls, outliers, drift), and generates visual reports. It supports modular profiling, CLI integration, expectation validation, and report generation for use in data validation pipelines.

Key Features:
- Dataset profiling for numerical and categorical columns
- Schema drift detection and field-level change audit
- Rule-based validation (mean, nulls, type)
- Visual HTML/Markdown report generation
- CI-compatible exit codes and dry-run simulation
- Modular CLI structure with snapshot and drift support

---

## Code Execution Screenshots

### Conversation 1: Execution Output  
![Conversation 1 Execution](https://drive.google.com/uc?id=1ceqIAlvaFfpEhS7B31F5i5Xz1giSdPVn)

### Conversation 2: Execution Output  
![Conversation 2 Execution](https://drive.google.com/uc?id=188mBHwMDzg0bJt_EYdtGdAsrGYbYYFus)

### Conversation 3: Execution Output  
![Conversation 3 Execution](https://drive.google.com/uc?id=1YLw1F4RdcBFnZcPxVZnY-FionMJ2FZJH)

### Conversation 4: Execution Output  
![Conversation 4 Execution](https://drive.google.com/uc?id=16SrvVBrH8AxcT1AEyPGT0xOLfo1QFsAn)

### Conversation 5: Execution Output  
![Conversation 5 Execution](https://drive.google.com/uc?id=1iEehz7HTJUwlGWlEvvETtuN_S6F2C6Br)

### Conversation 6: Execution Output  
![Conversation 6 Execution](https://drive.google.com/uc?id=1CphX7jmyZ9jwT_hqGSnG80T-D0tcK-7Y)

### Conversation 7: Execution Output  
![Conversation 7 Execution](https://drive.google.com/uc?id=1jV4_FPpT3jtLSQcxrQbfHYNN3mtEpUwZ)

### Conversation 8: Execution Output  
![Conversation 8 Execution](https://drive.google.com/uc?id=1jOzooW6PIMzje-vVwFkJFtiat7bn2nQN)

---

## Unit Test Outputs and Coverage

### Conversation 1 Test Results  
- **Tests 1–2**: Load `basic.csv`, profile `age` column, validate nulls = 0  
![Test 1–2](https://drive.google.com/uc?id=1NfESHpbhPoEwZzBtm9q_xWCEB18SOgB8)

### Conversation 2 Test Results  
- **Tests 3–4**: Simulate drift by comparing column sets between `tc1_v1.csv` and `tc1_v2.csv`  
![Test 3–4](https://drive.google.com/uc?id=1gz4DXgC6JQp9862OQspfH-JvDnz6GzLk)

### Conversation 3 Test Results  
- **Tests 5–6**: Evaluate rule checks on `age` column (null rate + mean threshold)  
![Test 5–6](https://drive.google.com/uc?id=14738y0IvMdULqc198Zo-oENvBac-Uc6d)

### Conversation 4 Test Results  
- **Tests 7–8**: Simulated explanations and fix hints for failing validations  
![Test 7–8](https://drive.google.com/uc?id=1OLtuzpPEAR2b333OE2mrHKpTUQhwMoDw)

### Conversation 5 Test Results  
- **Tests 9–10**: HTML visual report creation via CLI fallback or dummy render  
![Test 9–10](https://drive.google.com/uc?id=1n2xVR9KHvmeYSDN2610-5vbwVs4tFJxu)

### Conversation 6 Test Results
- Placeholder for advanced CI and HTML snapshot validation  
![Test 11–12](https://drive.google.com/uc?id=1CRqfaQrtXUcNHAi7P20ykSM87hSsK9g-)

### Conversation 7 Test Results
- Placeholder for snapshot comparison and drift timeline audit  
![Test 13–14](https://drive.google.com/uc?id=1QqaWE4pZQARmYRQnzp9rW2pKnMrsib56)

### Conversation 8 Test Results
- Placeholder for grouped expectation and conditional rule validation  
![Test 15–16](https://drive.google.com/uc?id=1zn-QTVO6uyiXDsq0sFpB5mJCogGxKm5m)

---

## Project Features Mapped to Conversations

- **Conversation 1**: Dataset discovery, profiling, type inference
- **Conversation 2**: Drift comparison logic, column metadata reuse
- **Conversation 3**: Rule expectation validation (nulls, means)
- **Conversation 4**: Violation explanation and fix hinting
- **Conversation 5**: Visual report generation (HTML)
- **Conversation 6**: CI workflow integration and audit threshold enforcement
- **Conversation 7**: Snapshot lineage tracking and drift regression history
- **Conversation 8**: Declarative validation and grouped rule handling

---

# Test Simulation Inputs

## Directory: `Output_code/code_inputs/py_tests/`
This directory contains Python scripts that simulate real audit workflows for dataset profiling, drift detection, rule validation, and visual report generation. These scripts validate the core system behavior in a production-like scenario.

### Files Included:
- `test_basic_profiling_and_schema_inference.py` → Profiles `basic.csv`, confirms schema inference and null count on numeric columns.  
- `test_drift_audit_between_versions.py` → Simulates drift audit between two dataset versions by comparing added/removed fields.  
- `test_rule_expectation_violation.py` → Validates rule logic against profiled `age` column, simulates threshold breaches and null rate checks.  
- `test_visual_html_report_generation.py` → Generates or simulates an HTML visual report for profiled dataset to verify visual output workflow.

### Usage:
Run each script manually or through pytest:
```bash
# Run manually
python Output_code/code_inputs/py_tests/test_basic_profiling_and_schema_inference.py
python Output_code/code_inputs/py_tests/test_drift_audit_between_versions.py
python Output_code/code_inputs/py_tests/test_rule_expectation_violation.py
python Output_code/code_inputs/py_tests/test_visual_html_report_generation.py
```

### Input Code Execution Screenshots

- `test_basic_profiling_and_schema_inference.py`  
  ![basic_profiling](https://drive.google.com/uc?id=1ykImszQCqovQDcQGkzXC77jPP65lExrG)

- `test_drift_audit_between_versions.py`  
  ![drift_audit](https://drive.google.com/uc?id=11n1CuFBLdDE58kYdBPn8k9JiCdx2KdzT)

- `test_rule_expectation_violation.py`  
  ![rule_violation](https://drive.google.com/uc?id=12a07bigIQnev9crUIOzpuYKOBDgV1-Ax)

- `test_visual_html_report_generation.py`  
  ![visual_html](https://drive.google.com/uc?id=1Xpu8VUKcamWaIgJEj1CWD8hiyJHJ_eKE)