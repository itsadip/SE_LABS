# Lab 4 – Vibe Coding: Balloon Pop

**Aditya Pradeep · PES2UG24AM900 · Section 5B** · Assigned repo: `SETAPESU26/05_balloon_pop` (task list in `README_original.md`)

## Deliverables

| Deliverable | Location |
|-------------|----------|
| a. Videos (before and after) | `videos/before_changes.mp4` (10 s), `videos/after_changes.mp4` (~11 s) |
| b. Updated code | `balloon-pop/` |
| c. Chat history | `ChatHistory.pdf` (source: `ChatHistory.md`) |

## Commits (one per task)

| Task | Change |
|------|--------|
| Task 1 – bug fix | `check_pop` now compares `dx²+dy²` with `radius²` (it used the plain radius), and pops the top-most balloon when two overlap |
| Task 2 – balloon types | normal (red, +10), bonus (gold `+`, +30), penalty (grey `−`, −15, score floored at 0), plus an on-screen legend |
| Task 3 – lives | 3 lives; each balloon that falls past the bottom costs 1 life; popping never does; game over at 0 |
| Task 4 – timed round | 30 s countdown (turns red under 5 s). The round ends on time-out or 0 lives and shows the final score; **R** or **Play Again** resets score, lives and timer |

## Run

```bash
cd balloon-pop
pip install -r requirements.txt
python main.py
```

The videos were captured from the real game code running headless with scripted mouse clicks. A red ✕ marks a click that missed; a green ring marks a click that popped a balloon.
