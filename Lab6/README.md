# Lab 6 – Code & Branch Coverage: Blood Donation Screening

**Aditya Pradeep · PES2UG24AM900 · Section 5B** · Assigned repo: `SETAPESU26/L6_L7_05_blood_donation_screening`

| Deliverable | File |
|-------------|------|
| Test cases for code (line) coverage | `CodeCoverageTest_PES2UG24AM900_blood_donation_screening.py` (11 tests) |
| Test cases for branch coverage | `BranchCoverageTest_PES2UG24AM900_blood_donation_screening.py` (39 tests) |
| Terminal output screenshots | `screenshots/02_code_coverage_100_percent.png`, `screenshots/03_branch_coverage_100_percent.png` (starting point: `01_initial_starter_test_coverage.png`) |
| Commits | one for the code-coverage tests and one for the branch-coverage tests |

## Results (`blood_donation_screening.py`)

| Suite | Line coverage | Branch coverage |
|-------|---------------|-----------------|
| Starter `test_blood_donation.py` | 47% | 43% (8 partial branches) |
| CodeCoverageTest | **100%** (45/45) | 99% (missing 26→15) |
| BranchCoverageTest | **100%** | **100%** (32/32 branches) |

The code-coverage suite runs every line, yet it still misses one branch. Low hemoglobin in a *standard* cohort (`if cohort_type == "high_altitude"` evaluating **False**) never happens in it, because the only low-Hb test used a high-altitude cohort. This is exactly the line-vs-branch gap the handout describes. The branch suite adds that case, plus empty cohort and donor lists, each side of the `or` conditions, the exact thresholds (age 17, weight 50, Hb 12.5 and 18.0, 3000 RPM) and the per-run reset of the centrifuge streak.

```bash
pip install coverage pytest
coverage run -m pytest CodeCoverageTest_PES2UG24AM900_blood_donation_screening.py && coverage report -m
coverage run --branch -m pytest BranchCoverageTest_PES2UG24AM900_blood_donation_screening.py && coverage report -m
```
