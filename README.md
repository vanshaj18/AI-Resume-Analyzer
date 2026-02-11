<!-- Improved compatibility of back to top link: See: https://github.com/othneildrew/Best-README-Template/pull/73 -->
<a id="readme-top"></a>

<!-- PROJECT LOGO / TITLE -->
<br />
<div align="center">
  <h3 align="center">AI Resume Analyzer</h3>

  <p align="center">
    Semantic, Technical, and Psychometric resume analysis with a Django UI, FastAPI backend, and Celery workers.
    <br />
    <a href="#getting-started"><strong>Get Started »</strong></a>
    <br />
    <br />
    <a href="#usage">Usage</a>
    &middot;
    <a href="#architecture">Architecture</a>
    &middot;
    <a href="#screenshots">Screenshots</a>
  </p>
</div>



<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li><a href="#about-the-project">About The Project</a></li>
    <li><a href="#built-with">Built With</a></li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
        <li><a href="#environment">Environment</a></li>
      </ul>
    </li>
    <li><a href="#architecture">Architecture</a></li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#project-structure">Project Structure</a></li>
    <li><a href="#screenshots">Screenshots</a></li>
    <li><a href="#tests">Tests</a></li>
  </ol>
</details>



<!-- ABOUT THE PROJECT -->
## About The Project

AI Resume Analyzer provides a full-stack pipeline to evaluate resumes using semantic, technical, and psychometric signals. It supports single-text analysis and async batch PDF processing with progress updates and a history view.

<p align="right">(<a href="#readme-top">back to top</a>)</p>



## Built With

* [Django][Django-url]
* [FastAPI][FastAPI-url]
* [Celery][Celery-url]
* [Redis][Redis-url]
* [Python][Python-url]

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- GETTING STARTED -->
## Getting Started

Follow these steps to run the app locally.

### Prerequisites

* Python 3.10+ (3.12 recommended)
* Redis 6+

### Installation

1. Create and activate a virtual environment
   ```bash
   python -m venv env
   source env/bin/activate
   ```
2. Install dependencies
   ```bash
   pip install -r requirements.txt
   ```

### Environment

Create `.env` using `env.example` as a reference.

```
GROQ_API_KEY=your_key
BACKEND_PORT=8001
FRONTEND_URL=http://localhost:8000
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/1
```

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- ARCHITECTURE -->
## Architecture

```
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
```

### Components

- **Django UI** (`ui/`): Single analysis form, batch upload, analytics view.
- **FastAPI Backend** (`analysis/`):
  - `POST /analysis` for synchronous JSON analysis
  - `POST /analysis/async` + `GET /analysis/status/{task_id}` for async batch pipeline
- **Celery Workers**:
  - Extraction queue: PDF bytes → text
  - Analysis queue: LLM analysis
  - Reporting queue: summary + score
- **Redis**:
  - Celery broker/result backend
  - Resume cache and intermediate outputs

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- USAGE -->
## Usage

### Quick start

Use the helper script to start Redis, workers, and servers.

```bash
cd project
chmod +x build.sh
./build.sh
```

### Manual start

1. Start Redis
   ```bash
   redis-server
   ```
2. Start Celery workers
   ```bash
   python manage.py collectstatic --noinput
   python manage.py migrate --noinput
   celery -A backend.celery_app worker --loglevel=info -Q extraction,analysis
   ```
3. Start FastAPI backend
   ```bash
   uvicorn analysis.app:app --host 127.0.0.1 --port 8001
   ```
4. Start Django frontend
   ```bash
   python manage.py runserver 127.0.0.1:8000
   ```

### Notes

- Single analysis: paste text and run.
- Batch analysis: upload multiple PDFs or a folder; progress appears per file.
- Threshold drives the pass/fail badge per file in the UI.

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- PROJECT STRUCTURE -->
## Project Structure

```
project/
  analysis/
    app.py
    services.py
    semantic.py
    technical.py
    psychometric.py
    tasks.py
    store.py
  backend/
    celery_app.py
  ui/
    templates/ui/index.html
    static/ui/styles.css
```

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- SCREENSHOTS -->
## Screenshots

* Landing Page
  ![Landing page](assets/landing.png)

* Single Analysis
  ![Single Analysis page](assets/single_upload.png)

* Batch Uploads
  ![Batch Uploads](assets/batch_upload.png)

* Analytics
  ![Analytics page](assets/analytics.png)

* Technical Docs
  ![Technical Docs](assets/technical_docs.png)

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- TESTS -->
## Tests

```bash
pytest backend/unit_test.py
```

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- MARKDOWN LINKS & IMAGES -->
[Django-url]: https://www.djangoproject.com/
[FastAPI-url]: https://fastapi.tiangolo.com/
[Celery-url]: https://docs.celeryq.dev/
[Redis-url]: https://redis.io/
[Python-url]: https://www.python.org/
