# Use-Case Flow Specification — UC-05: Grade Project Using Digital Rubric

**Name:** Aditya Pradeep  **SRN:** PES2UG24AM900  **System:** Student Project Portfolio & Showcase App

| Field | Detail |
|-------|--------|
| **Use-Case ID / Name** | UC-05 — Grade Project Using Digital Rubric |
| **Primary Actor** | Panel Judge |
| **Secondary Actor** | OTP / Identity Service (for multi-factor authentication) |
| **Related Requirements** | FR-003 (digital rubric), NFR-002 (MFA, audit log) |
| **Relationships** | «include» *Authenticate with MFA*; «extend» *Add Improvement Comments* |
| **Trigger** | The judge opens a project from their "Assigned Projects" list during the judging window. |

**Preconditions**

1. The judge has an active account and has been assigned to the project's category by the expo organisers.
2. The project's showcase profile is published, i.e. its GitHub repository has been verified (UC-02).
3. The judging window is open and the judge has not already submitted a grade for this project.

**Postconditions (success)**

1. A locked, read-only grade sheet is stored with each criterion score, the weighted total and the judge's comments.
2. An append-only audit-log entry (judge ID, project ID, timestamp, hash of the scores) is written.
3. The project's aggregate judge score is recalculated and the project moves to "Graded by *n* of *m* judges".

**Main Success Scenario**


| # | Actor / System | Action |
|------|----------------|--------|
| 1 | Judge | Logs in with a username and password. |
| 2 | System | «include» *Authenticate with MFA*: sends an OTP through the Identity Service, and the judge enters it. The system verifies it. |
| 3 | System | Shows the judge's dashboard, listing only the projects assigned to them, with their grading status. |
| 4 | Judge | Selects a project. |
| 5 | System | Shows the project profile (abstract, media, repository link) beside the rubric: Innovation 30%, Technical Depth 30%, Presentation 20%, Impact 20%. |
| 6 | Judge | Enters a score from 0 to 10 for each criterion. |
| 7 | System | Validates each score (an integer from 0 to 10, with no criterion left blank) and shows the weighted total live. |
| 8 | Judge | Optionally «extend» *Add Improvement Comments* for the team, then clicks **Submit Final Grade**. |
| 9 | System | Asks for confirmation ("Grades cannot be edited after submission"). |
| 10 | Judge | Confirms. |
| 11 | System | Saves the grade sheet, locks it, writes the audit-log entry, updates the aggregate, and shows "Grade submitted successfully". |

**Alternate Flow A1 — Incomplete or invalid rubric (branches from step 7/10)**


| # | Action |
|------|--------|
| A1.1 | The judge clicks Submit with a criterion left blank or a value outside 0–10 (e.g. 12). |
| A1.2 | The system blocks the submission, highlights the invalid fields in red, and shows "All criteria must be scored between 0 and 10". |
| A1.3 | The judge corrects the scores. The system saves a draft automatically every 30 seconds, so no input is lost. |
| A1.4 | The flow resumes at step 8 of the Main Success Scenario. |

**Exception — Judging window closed:** if the deadline passes before step 10, the system saves the sheet as a draft, rejects the submission with "Judging is closed", and notifies the organisers.
