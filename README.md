# AI Resume Analyzer

Semantic, Technical, and Psychometric resume analysis with a Django UI, FastAPI backend, and Celery workers.

## Architecture
┌──────────────────────────────────────┐
│  AI Resume Analyzer                  │
│  Semantic & Psychometric Insights    │
└──────────────────────────────────────┘

┌───────────────┐  ┌─────────────────┐
│ Resume Input  │  │ AI Configuration │
│               │  │                 │
└───────────────┘  └─────────────────┘

        [ Run Analysis ]

┌──────────────────────────────────────┐
│ Batch Processing (Parallel Jobs)     │
└──────────────────────────────────────┘

┌──────────────────────────────────────┐
│ Live Status & Progress               │
└──────────────────────────────────────┘

┌──────────────────────────────────────────────────┐
│ Results (Technical | Semantic | Psychometric)    │
└──────────────────────────────────────────────────┘

## Components
- **Frontend (Django UI)**: `frontend/`
  - Single analysis form and batch upload UX
  - Progress polling + per-file status
- **Backend (FastAPI)**: `backend/`
  - `/analysis` for synchronous JSON analysis
  - `/analysis/async` + `/analysis/status/{task_id}` for async batch pipeline
- **Workers (Celery)**:
  - Extraction queue: PDF bytes → text
  - Analysis queue: LLM analysis
  - Reporting queue: summary + score
- **Redis**:
  - Celery broker/result backend
  - Resume cache and intermediate outputs (see `backend/analysis/store.py`)

## Setup
### Requirements
- Python 3.10+ (3.12 recommended)
- Redis 6+

### Install
```bash
python -m venv env
source env/bin/activate
pip install -r requirements.txt
```

### Environment
Create a `.env` with:
```
GROQ_API_KEY=your_key
BACKEND_PORT=8001
FRONTEND_URL=http://localhost:8000
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/1
```

## Run
### 1) Start Redis
```bash
redis-server
```

### 2) Start Celery workers
```bash
python manage.py collectstatic --noinput
python manage.py migrate --noinput
celery -A backend.celery_app worker --loglevel=info -Q extraction,analysis
```

### 3) Start FastAPI backend
```bash
uvicorn analysis.app:app --host 127.0.0.1 --port 8001
```

### 4) Start Django frontend
```bash
python manage.py runserver 127.0.0.1:8000
```

## Usage
- **Single analysis**: paste text and run.
- **Batch analysis**: upload multiple PDFs or a folder; progress appears per file.
- **Threshold**: used for pass/fail badge (green tick/red x) per file.

## Project Structure
```
backend/
  analysis/
    semantic.py
    technical.py
    psychometric.py
    services.py
    tasks.py
    store.py
  app.py
  celery_app.py
frontend/
  ui/
    templates/ui/index.html
    static/ui/styles.css
```

## Notes
- The batch pipeline is:
  1. Store PDF in Redis
  2. Extract text (Celery extraction queue)
  3. Run analysis (Celery analysis queue)
  4. Generate report (Celery reporting queue)
- Frontend polling hits `/analysis/status/{task_id}` for progress updates.

## Tests
```bash
pytest backend/unit_test.py
```
