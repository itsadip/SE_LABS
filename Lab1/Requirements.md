# Lab 1 – Requirements Engineering & UML Use-Case Modelling

**Name:** Aditya Pradeep  **SRN:** PES2UG24AM900  **Section:** 5B
**Problem Statement #04:** Student Project Portfolio & Showcase App (Campus & Academic Operations)

## 1. Problem Context

Annual project expos need one central showcase. Student teams submit multimedia artifacts there, panel judges grade projects with digital rubrics, and the public votes under strict anti-sybil protection.

**Actors**

| Actor | Kind | Role |
|-------|------|------|
| Student Team | Primary | Creates the showcase profile, uploads artifacts, and views feedback and results |
| Panel Judge | Primary | Reviews assigned projects and grades them with the digital rubric |
| Public Visitor | Primary | Browses the catalogue, casts a verified vote, and views the leaderboard |
| GitHub API | Secondary (system) | Confirms that a submitted repository URL exists and is public |
| OTP / Identity Service | Secondary (system) | Sends and checks one-time codes for verifying voters and judges |

## 2. Functional Requirements

| ID | Type | Description | Priority | Acceptance Criteria | Rationale |
|----|------|-------------|----------|---------------------|-----------|
| FR-001 | Functional | The system shall let student teams create showcase profiles with a title, an abstract summary (≤ 300 words), team members, a demo-video link and a verified GitHub repository URL. | High | **Pass:** the profile is published to the showcase catalogue only after the GitHub API confirms that the repository exists and is public. **Fail:** a malformed URL (e.g. `htp:/github`) or a non-existent or private repository is accepted. | The profile is the core artifact of the expo. Verifying the repository keeps fake or empty projects out of the catalogue. |
| FR-002 | Functional | The system shall let a team upload multimedia artifacts (PNG/JPG images, a PDF poster, and an MP4 video or YouTube link) to its profile, with each file ≤ 50 MB and at most 10 files per project. | High | **Pass:** valid files upload and appear on the profile with thumbnails. A file larger than 50 MB or of an unsupported type is rejected with a clear error message. **Fail:** an `.exe` or a 200 MB file is stored. | Judges and visitors rely on rich media to understand a project. Limits on size and type protect storage and stop malware uploads. |
| FR-003 | Functional | The system shall present each panel judge with a digital rubric for every project assigned to them: weighted criteria such as Innovation 30%, Technical Depth 30%, Presentation 20% and Impact 20%, each scored 0–10 with a mandatory comment. The system shall lock the grade sheet once it is submitted. | High | **Pass:** the weighted total is calculated automatically, an incomplete rubric cannot be submitted, and a submitted sheet becomes read-only. **Fail:** a judge can grade a project not assigned to them, or can edit a grade after submission. | Digital rubrics make grading consistent, auditable and quick to aggregate across judges. |
| FR-004 | Functional | The system shall allow a public visitor to cast exactly one vote per project category, after verifying their identity with a one-time password (OTP) sent to a unique phone number or institutional email. Rate limiting and device fingerprinting shall be used to detect sybil (fake-identity) voting. | High | **Pass:** a second vote from the same verified identity in the same category is rejected, and more than 5 OTP requests per device per hour are blocked. **Fail:** the same phone or email can vote twice, or a vote is counted without OTP verification. | Public voting is only meaningful if each person votes once. Anti-sybil controls are an explicit requirement of the problem statement. |
| FR-005 | Functional | The system shall show a live leaderboard per category that ranks projects by public votes, and shall publish final results that combine the judges' rubric scores (70%) with the normalised public vote (30%) once the organisers close judging. | Medium | **Pass:** the leaderboard reflects a new vote within 2 seconds, and final scores match a manual calculation from the stored rubric and vote data. **Fail:** results are visible before judging closes, or the ranking disagrees with the stored scores. | A transparent leaderboard keeps the public engaged. A combined, reproducible formula makes the final result fair and defensible. |

## 3. Non-Functional Requirements

| ID | Type | Description | Priority | Acceptance Criteria | Rationale |
|----|------|-------------|----------|---------------------|-----------|
| NFR-001 | Performance & Scalability | Public voting and leaderboard calculations shall update in real time. The 95th-percentile API response time for the vote and leaderboard endpoints shall stay under 300 ms with 2,000 concurrent users. | High | **Pass:** a load test (e.g. JMeter or k6 with 2,000 virtual users for 10 minutes) shows p95 latency < 300 ms and an error rate < 1%. **Fail:** p95 latency ≥ 300 ms, or requests time out at peak load. | Voting traffic spikes sharply during the live expo. A slow system frustrates voters and lowers participation. |
| NFR-002 | Security & Integrity | All traffic shall use TLS 1.2 or later. Judge accounts shall require multi-factor authentication. Voter identifiers (phone/email) shall be stored only as salted hashes. Every vote and grade shall be written to an append-only audit log. | High | **Pass:** a security scan (OWASP ZAP) finds no high-severity issues, plain-HTTP requests are redirected to HTTPS, and the database stores no raw phone numbers or emails. **Fail:** an audit-log record can be edited or deleted, or a judge can log in with only a password. | Grades and votes decide awards, so they must be tamper-proof. Voters' personal data must be protected under data-privacy rules. |

## 4. Deliverables in this folder

| File | Contents |
|------|----------|
| `Requirements.md` | This requirements table (5 FRs, 2 NFRs) |
| `UseCaseDiagram.png` / `UseCaseDiagram.svg` | UML use-case diagram (all actors, «include» and «extend» relationships) |
| `UseCase_Flow_Specification.md` / `.pdf` | One-page flow specification for *UC-05: Grade Project Using Digital Rubric* |
