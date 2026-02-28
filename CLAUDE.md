# HoopShot — Basketball Game App

## Architecture
Three-component system:
- **Backend**: FastAPI + SQLite (port 8000)
- **Frontend**: Next.js (port 3000)
- **iOS**: SwiftUI app connecting to backend

## Development

### Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
# API docs at http://localhost:8000/docs
```

### Frontend
```bash
cd frontend
npm install
npm run dev
# Visit http://localhost:3000
```

### Docker
```bash
# Backend
docker build -t hoopshot-backend ./backend
docker run -p 8000:8000 hoopshot-backend

# Frontend
docker build -t hoopshot-frontend ./frontend
docker run -p 3000:3000 hoopshot-frontend
```

### iOS
Open `ios/HoopShot/HoopShot.xcodeproj` in Xcode, run on iPhone simulator.
Configure `API_BASE_URL` in `Info.plist` (default: `http://localhost:8000`).

## API Endpoints
| Method | Path | Auth | Purpose |
|--------|------|------|---------|
| POST | /auth/register | No | Create account |
| POST | /auth/login | No | Returns JWT |
| GET | /auth/me | JWT | Current user info |
| POST | /scores | JWT | Submit game score |
| GET | /scores/me | JWT | User's score history |
| GET | /scores/leaderboard | No | Top 10 scores |

## Data
SQLite database stored at `backend/data/hoopshot.db`.

## Policy as Code
Policies live in `policies/*.yaml` and are enforced by `scripts/check_policies.py`.

```bash
# Run all automated policy checks
python3 scripts/check_policies.py

# Strict mode (also lists manual-review items — use before releases)
python3 scripts/check_policies.py --strict
```

Policy files:
- `policies/security.yaml` — secrets, SQL injection, CORS, auth guards
- `policies/api_design.yaml` — HTTP conventions, health endpoint, /docs tags
- `policies/code_quality.yaml` — bare except, TODO comments, force-unwraps, any-types
- `policies/data.yaml` — PII, password hashing, JWT expiry, .gitignore
- `policies/git_workflow.yaml` — commit format, branch protection, PR requirements, Kubernetes deployment gates
- `policies/testing.yaml` — required test files, coverage, CI test ordering

Exit code 0 = all automated checks pass. Exit code 1 = failures that must be fixed before merge.

## Running Backend Tests
```bash
cd backend
pip install -r requirements.txt pytest httpx
pytest tests/ -v
pytest tests/ --cov=app --cov-report=term-missing
```
