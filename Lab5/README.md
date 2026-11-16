# Lab 5 – Static Code Analysis: Fitness Club Class Booking Ledger

**Aditya Pradeep · PES2UG24AM900 · Section 5B** · Assigned repo: `SETAPESU26/L5_04_fitness_booking` (original instructions in `README_original.md`)

| Deliverable | File |
|-------------|------|
| Cleaned code (15 issues fixed) | `gym_system.py` |
| Issue table | `issues.md` |
| Reflection answers | `reflection.md` |
| Reports **before** | `reports/before/pylint_report.txt`, `bandit_report.txt`, `flake8_report.txt` (+ `program_output.txt`) |
| Reports **after** | `reports/after/pylint_report.txt`, `bandit_report.txt`, `flake8_report.txt` (+ `program_output.txt`) |

| Tool | Before | After |
|------|--------|-------|
| Pylint | 6.60/10 | **10.00/10** |
| Bandit | 1 High (B605) | **No issues** |
| Flake8 | 10 | **0** |

Commits: there is one commit for each tool's fixes (Bandit → Pylint → Flake8), plus one for the logic bugs found by running the program.

```bash
python -m venv venv && source venv/bin/activate
pip install pylint bandit flake8
pylint gym_system.py > pylint_report.txt
bandit -r gym_system.py > bandit_report.txt
flake8 gym_system.py > flake8_report.txt
```
