# Lab 5 – Reflection

**Aditya Pradeep · PES2UG24AM900 · Section 5B**

### 1. Which issues were the easiest to fix, and which were the hardest? Why?

**Easiest:** the Flake8 formatting issues (E302/E305 blank lines) and the simple Pylint style warnings: renaming `addMembers` to `add_members`, switching to an f-string, using `.items()`, and adding docstrings. Each is mechanical, local to one line, and cannot change behaviour.

**Hardest:** the Bandit **B605** shell-injection issue and the bugs no tool reported. For B605, removing `os.system` was not enough on its own. I had to reproduce what `rm -f old_*.json` did (glob matching, ignoring missing files) in pure Python, and decide how far to trust the `prefix` argument, so I added a whitelist regex. The logic bugs (the off-by-one capacity check, bookings into a non-existent "Pilates" class, negative capacity, the crash on non-numeric input) were harder still. I only found them by **running the program and reading its output**: Yoga showed 4 members for 3 seats. All three tools scored the code as clean even while it produced wrong results.

### 2. Did the static analysis tools report any false positives? If so, describe one example.

No finding was strictly false in this file, but some are **context-dependent**:

* **Bandit B605** would have been a false positive if the command string were a hard-coded constant. Bandit flags *any* `os.system` call. Here the prefix comes from a parameter, so the warning was a real issue.
* **Pylint C0116 (missing docstring)** on a tiny, self-explanatory function such as `set_capacity` is a style preference rather than a defect.
* **Flake8 E722 and Pylint W0702** reported the *same* bare `except` twice. This is duplication between tools rather than a false positive, but it shows why the reports need to be cross-checked instead of counted.

The opposite problem, **false negatives**, mattered more: none of the tools caught the five logic bugs (issues 11-15 in `issues.md`).

### 3. How would you integrate static analysis tools into your actual software development workflow?

* **Locally:** run the tools on every commit with a `pre-commit` hook (Flake8 and Bandit fast checks, Pylint on the changed files), plus editor integration (VS Code Pylint/Flake8 extensions) so issues appear while typing.
* **In CI (GitHub Actions):** a job that runs `flake8`, `bandit -r . -ll` (fail on medium or higher severity) and `pylint --fail-under=9.5` on every push and pull request. A merge is blocked if any of them fails, and the reports are uploaded as build artifacts.
* **Configuration in the repository:** `.pylintrc` and `setup.cfg` (Flake8) settings, so everyone runs the same rules. Any `# nosec` or `# pylint: disable=` must carry a justification comment and be reviewed.
* **Alongside tests:** static analysis complements, but does not replace, unit tests and actually running the code. This lab showed that clearly.

### 4. What tangible improvements did you observe in the code quality, readability, or potential robustness after applying the fixes?

* **Security:** no shell is spawned, so the command-injection vector (CWE-78) is gone. Bandit now reports *No issues identified*.
* **Correctness:** class capacities are enforced exactly (Yoga 3/3, HIIT 2/2). Unknown classes, invalid IDs, duplicate bookings and negative capacities are rejected with clear messages. The shared mutable default no longer leaks log entries between calls.
* **Robustness:** bad input (`abc`, `-3`, `²`, `99999999999`) no longer crashes or hangs the program. The export file is closed properly, written as UTF-8, and pretty-printed. Importing the module no longer runs `main()`.
* **Readability and maintainability:** PEP 8 formatting, snake_case names, f-strings and docstrings on every function. The Pylint score went from **6.60 to 10.00/10**, and Flake8 went from **10 findings to 0**.
