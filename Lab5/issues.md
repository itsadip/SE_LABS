# Lab 5 – Issue Table: `gym_system.py` (Fitness Club Class Booking Ledger)

**Aditya Pradeep · PES2UG24AM900 · Section 5B** · Assigned repo: `SETAPESU26/L5_04_fitness_booking`

| | Before | After |
|---|---|---|
| Pylint score | **6.60 / 10** | **10.00 / 10** |
| Bandit | 1 issue (**High** severity, High confidence) | No issues identified |
| Flake8 | 10 findings | 0 findings |

Line numbers refer to the **original** file (see `reports/before/`).

## Issues reported by the tools (high and medium severity first)

| # | Issue | Tool / Code | Type | Line(s) | Description | Fix Approach |
|---|-------|-------------|------|---------|-------------|--------------|
| 1 | Shell command injection | Bandit **B605** (High/High, CWE-78) | Security | 36 | `os.system("rm -f " + prefix + "*.json")` builds a shell command from a parameter. A prefix like `"x; rm -rf ~ #"` would run arbitrary commands. | Removed the shell entirely: matching files are found with `glob.glob(prefix + "*.json")` and deleted with `os.remove()`. The prefix is also checked against `[A-Za-z0-9_-]+`. |
| 2 | Mutable default argument | Pylint **W0102** dangerous-default-value | Bug | 8 | `attendance_log=[]` is created once and shared by every call, so log entries leak between unrelated bookings. | Default changed to `None`, with `attendance_log = []` created inside the function. |
| 3 | Bare `except:` | Pylint **W0702** / Flake8 **E722** | Bug | 20-22 | Catches *everything*, including `KeyboardInterrupt`, `SystemExit` and programming errors, and hides the real reason a cancel failed. | Catch only `KeyError` (unknown class) and `ValueError` (member not booked), with a specific message for each. |
| 4 | File opened without `with`/encoding | Pylint **R1732** consider-using-with, **W1514** unspecified-encoding | Bug / Resource leak | 32-33 | `f = open(file, "w")` is never closed, so the JSON may not be flushed to disk. The platform-default encoding makes the output non-portable. | `with open(file, "w", encoding="utf-8") as f:` |
| 5 | Function naming | Pylint **C0103** invalid-name | Style | 27 | `addMembers` is camelCase; PEP 8 wants snake_case. | Renamed to `add_members` and updated the callers. |
| 6 | Old-style `%` formatting | Pylint **C0209** consider-using-f-string | Style | 15 | `"%s -> %s" % (...)` | `f"{member_id} -> {class_name}"` |
| 7 | Iterating dict keys then indexing | Pylint **C0206** consider-using-dict-items | Style / Perf | 39-40 | `for c in rosters: ... rosters[c]` does a second lookup per key. | `for class_name, members in rosters.items():` |
| 8 | Missing docstrings | Pylint **C0114 / C0116** | Documentation | 1, 8, 18, 24, 27, 31, 35, 38, 42 | No module or function documentation. | Added a module docstring and a one-line docstring to every function. |
| 9 | Blank lines between functions | Flake8 **E302** (×8) | Style (PEP 8) | 8, 18, 24, 27, 31, 35, 38, 42 | Top-level definitions need 2 blank lines before them. | Inserted the missing blank lines. |
| 10 | Blank lines after functions / module-level call | Flake8 **E305** | Style (PEP 8) | 58 | `main()` ran at import time, right after a function. | Added 2 blank lines and wrapped the call in `if __name__ == "__main__":` so importing the module has no side effects. |

## Logic bugs found by running the program (not flagged by any tool)

| # | Issue | Type | Line(s) | Description | Fix Approach |
|---|-------|------|---------|-------------|--------------|
| 11 | Off-by-one capacity check | Logic bug | 11 | `len(roster) > capacity` lets one extra member in: **Yoga ended with 4 members for 3 seats**. | Changed to `>=`. |
| 12 | Booking into an undefined class | Logic bug | 9-11 | `class_capacity.get(name, 0)` combined with `0 > 0` being False meant **"Pilates" (not offered) accepted M5**. | Reject any class not in `class_capacity` ("Unknown class"). |
| 13 | Invalid / duplicate member IDs | Input validation | 8, 47 | The integer `55` was stored as a member ID, and the same member could be booked twice. | Member ID must be a non-empty string; duplicate bookings are rejected. |
| 14 | Negative capacity accepted | Input validation | 24-25, 49 | `set_capacity("Spin", -2)` stored −2 seats. | `set_capacity` accepts only an `int >= 0` (bools rejected) and returns False otherwise. |
| 15 | Crash and hang on walk-in input | Input validation / robustness | 52-53 | `int("abc")` raised **ValueError** and crashed. `-3` was silently ignored, and a huge number would loop billions of times. | `parse_guest_count()` accepts only ASCII digits (Enter means 1) and prints a helpful message otherwise. `add_members` stops as soon as the class is full, and guest IDs are unique across calls. |

## Commits

| Commit | What |
|--------|------|
| `Lab 5: Add original gym_system.py with before … reports` | Baseline plus `reports/before/*` |
| `Lab 5 (Bandit): Replace os.system shell call …` | Issue 1 |
| `Lab 5 (Pylint): Fix Pylint warnings, raising the score from 6.60 to 10.00` | Issues 2-8 |
| `Lab 5 (Flake8): Fix PEP 8 blank-line issues` | Issues 9-10 |
| `Lab 5: Fix booking logic bugs found by running the program` | Issues 11-15 |
| `Lab 5: Add after reports, issue table and reflection` | `reports/after/*`, this file, `reflection.md` |
