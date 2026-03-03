# HoopShot

A full-stack basketball shot-tracking game with an iOS SwiftUI client, a Next.js web dashboard, and a FastAPI backend — built with policy-as-code governance and a merge audit trail baked in from day one.

---

## Goal

HoopShot lets players shoot virtual hoops on their iPhone, tracks every game score, and surfaces results on a live leaderboard. Beyond the game itself the project is a reference implementation for:

- **Policy-as-code** — every merge is checked against security, API design, data, testing, and git workflow rules before it can land
- **Merge audit trail** — every push to `main` writes a content hash checkpoint to the game DB and a PR artifact hash + summary to a separate audit DB, giving a tamper-evident history of what shipped and why

---

## Architecture

```
┌─────────────────────────────────────────────────────┐
│  iOS (SwiftUI)          Frontend (Next.js :5678)     │
│  GameView               LoginForm                    │
│  LoginView    ────────▶ ScoreDashboard               │
│  ScoreSummaryView       Leaderboard                  │
└────────────┬────────────────────┬────────────────────┘
             │  HTTP/JSON         │  HTTP/JSON
             ▼                    ▼
     ┌────────────────────────────────────┐
     │        Backend  (FastAPI :8765)    │
     │  /auth/register  /auth/login       │
     │  /auth/me        /scores           │
     │  /scores/me      /scores/leaderboard│
     │  /health                           │
     └──────────────┬─────────────────────┘
                    │  SQLAlchemy ORM
          ┌─────────┴──────────┐
          ▼                    ▼
   hoopshot.db           pr_audit.db
   (game data +          (PR approval
    merge checkpoints)    artifact hashes)
```

| Component | Stack | Port |
|-----------|-------|------|
| Backend | FastAPI, SQLAlchemy, SQLite, passlib/bcrypt, python-jose | 8765 |
| Frontend | Next.js 14, TypeScript | 5678 |
| iOS | SwiftUI, URLSession | — |

---

## API Endpoints

| Method | Path | Auth | Purpose |
|--------|------|------|---------|
| POST | `/auth/register` | No | Create account |
| POST | `/auth/login` | No | Returns JWT |
| GET | `/auth/me` | JWT | Current user info |
| POST | `/scores` | JWT | Submit game score |
| GET | `/scores/me` | JWT | User's score history |
| GET | `/scores/leaderboard` | No | Top 10 scores |
| GET | `/health` | No | Health check |

JWT tokens expire after 7 days. All auth-required endpoints use `Depends(get_current_user)`.

---

## Data Schemas

### `users`
| Column | Type | Notes |
|--------|------|-------|
| id | INTEGER PK | |
| username | STRING | unique, indexed |
| hashed_password | STRING | bcrypt, cost 12 |
| created_at | DATETIME | UTC |

### `scores`
| Column | Type | Notes |
|--------|------|-------|
| id | INTEGER PK | |
| user_id | INTEGER FK | → users.id |
| score | INTEGER | points (2 per basket) |
| shots_taken | INTEGER | |
| shots_made | INTEGER | |
| created_at | DATETIME | UTC |

### `merge_checkpoints` (hoopshot.db)
| Column | Type | Notes |
|--------|------|-------|
| id | INTEGER PK | |
| commit_sha | STRING | unique, indexed |
| content_hash | STRING | SHA256 of all tracked files |
| branch | STRING | |
| author | STRING | |
| message | STRING | commit subject |
| merged_at | DATETIME | UTC |

### `pr_approvals` (pr_audit.db)
| Column | Type | Notes |
|--------|------|-------|
| id | INTEGER PK | |
| pr_number | INTEGER | |
| pr_title | STRING | |
| pr_author | STRING | |
| artifact_hash | STRING | SHA256 of changed files only |
| summary | TEXT | full PR body |
| approved_at | DATETIME | UTC |

---

## Policy as Code

Policies live in `policies/*.yaml` and are enforced by `scripts/check_policies.py`.

```bash
python3 scripts/check_policies.py          # automated checks
python3 scripts/check_policies.py --strict # include manual-review items
```

| File | What it governs |
|------|-----------------|
| `security.yaml` | No hardcoded secrets, no plaintext passwords, no SQL injection, CORS, JWT |
| `api_design.yaml` | HTTP conventions, `/health` endpoint, `/docs` tags |
| `code_quality.yaml` | No bare except, no TODO comments, no force-unwraps, no `any` types |
| `data.yaml` | PII minimisation, bcrypt hashing, JWT expiry, `.gitignore` coverage |
| `git_workflow.yaml` | Commit format, branch protection, PR requirements, merge audit scripts |
| `testing.yaml` | Required test files, coverage ≥ 80%, CI gate ordering |

Exit code `0` = all automated checks pass. Exit code `1` = must fix before merge.

### Merge audit CI

`.github/workflows/merge-checkpoint.yml` triggers on every push to `main` and runs `scripts/record_merge.py`, which:

1. Computes a **content hash** (SHA256 over all tracked files) → written to `merge_checkpoints`
2. Computes an **artifact hash** (SHA256 over only the changed files) → written to `pr_approvals`
3. Captures PR number, title, author, and full description from `github.event`

---

## Running Locally

### Backend
```bash
cd backend
pip install -r requirements.txt
python3 -m uvicorn app.main:app --port 8765 --reload
# http://localhost:8765/docs
```

### Frontend
```bash
cd frontend
npm install
npm run dev -- --port 5678
# http://localhost:5678
```

### iOS
Open `ios/HoopShot/HoopShot.xcodeproj` in Xcode, select an iPhone simulator, and run (⌘R).
`API_BASE_URL` is set to `http://localhost:8765` in `HoopShot/Info.plist`.

### Run policy checks
```bash
python3 scripts/check_policies.py
```

### Run backend tests
```bash
cd backend
pytest tests/ -v
pytest tests/ --cov=app --cov-report=term-missing
```

---

## How the Game Works

- 30-second shot clock
- Swipe up on the ball to shoot — angle and power determine if it goes in
- Each basket = 2 points
- At the end of a round, tap **Save Score** to POST the result to the backend
- Scores appear on the web dashboard leaderboard in real time

---

## Todo

### Near-term
- [ ] Register flow on iOS (currently web-only)
- [ ] Restrict CORS to known origins before any public deployment
- [ ] Inject `SECRET_KEY` via env var (currently hardcoded placeholder)
- [ ] Add sound effects and haptic feedback to the iOS game
- [ ] Frontend auto-refresh leaderboard (polling or WebSocket)
- [ ] `gh` CLI setup for automated repo creation in CI

### Active Learning (coming later)
- [ ] **Shot prediction model** — train a lightweight on-device Core ML model on `(swipe_angle, power_ratio) → made/missed` to personalise difficulty
- [ ] **Adaptive difficulty** — adjust the scoring window dynamically based on rolling accuracy so the game stays challenging at any skill level
- [ ] **Player embeddings** — represent each player as a latent vector derived from their shot history; use cosine similarity to surface "players like you" on the leaderboard
- [ ] **Anomaly detection on scores** — flag statistically improbable score submissions (e.g. 60 shots in 30 seconds) using an isolation forest trained on legitimate game sessions
- [ ] **Merge risk scoring** — extend the audit system to score each PR's artifact hash diff against a learned baseline of "safe" change patterns; surface high-risk merges for extra review
