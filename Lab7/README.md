# Lab 7 – Fuzz Testing with Hypothesis: Blood Donation Processor

**Aditya Pradeep · PES2UG24AM900 · Section 5B** · Assigned repo: `SETAPESU26/L6_L7_05_blood_donation_screening`

| # | Deliverable | File |
|---|-------------|------|
| 1 | PDF document with screenshots | `Lab7_Fuzz_Testing_Report.pdf` (source: `.md`; images in `screenshots/`) |
| 2 | Fixed application script | `processor.py` |
| 3 | Updated test file | `test_processor.py` (3 completed starter tests + 9 targeted/property fuzz tests) |

| Run | Result |
|-----|--------|
| `pytest test_processor.py` against the original `processor.py` | **9 failed, 3 passed** (crashes: KeyError, IndexError, AttributeError, ZeroDivisionError, ValueError; wrong answers on `0/1` and `|0|NAN`) |
| `pytest test_processor.py` against the fixed `processor.py` | **12 passed** |

```bash
pip install hypothesis pytest
python processor.py
pytest test_processor.py
```
