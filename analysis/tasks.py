import base64
import json
import logging
import os
from analysis.store import load_pdf, store_extracted_text, load_extracted_text, store_analysis, load_analysis
from backend.celery_app import celery_app
from .services import run_full_analysis
from .pdf_utils import pdf_bytes_to_text

logger = logging.getLogger("backend.analysis.tasks")

def _log_async_run(*, file_name: str | None, ai_model: str | None, temperature: float | None,
                   threshold: int | None, document_length: int, result: dict):
    try:
        if not os.getenv("DJANGO_SETTINGS_MODULE"):
            os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")
        import django
        django.setup()
        from ui.models import AnalysisRun
        AnalysisRun.objects.create(
            source="pdf",
            file_name=file_name or "upload.pdf",
            ai_model=ai_model or "llama-3.1-8b-instant",
            temperature=temperature or 0.2,
            threshold=threshold or 50,
            has_pdf=True,
            document_length=document_length,
            result_json=json.dumps(result),
        )
    except Exception:
        logger.exception("async_run_log_failed")


@celery_app.task(name="analysis.tasks.extract_text_task", bind=True)
def extract_text_task(self, file_id: str, file_name: str | None = None):
    try:
        self.update_state(
            state="STARTED",
            meta={"stage": "extracting"}
        )

        file_bytes = load_pdf(file_id)
        text = (pdf_bytes_to_text(file_bytes) or "").strip()
        if not text:
            raise ValueError("No extractable text found in PDF.")
        # store the extracted text
        store_extracted_text(file_id, text)
        return {"file_id": file_id, "file_name": file_name}
    
    except Exception:
        logger.exception("extract_pdf_text_failed", extra={"file_id": file_id})
        raise

@celery_app.task(name="analysis.tasks.analyze_resume_task", bind=True, rate_limit="5/m")
def analyze_resume_task(
    self,
    previous: dict,
    ai_model: str | None = None,
    temperature: float | None = None,
    threshold: int | None = None,
    criteria: dict | None = None,
    jd_prompt: str | None = None,
):
    try:
        self.update_state(
            state="STARTED",
            meta={"stage": "analysis"}
        )

        file_id = previous["file_id"]
        text = load_extracted_text(file_id)
        result = run_full_analysis(
            text,
            model=ai_model,
            temperature=temperature,
            threshold=threshold,
            criteria=criteria,
            jd_prompt=jd_prompt,
            task=self,
        )
        store_analysis(file_id, "full", result)
        return {
            "file_id": file_id,
            "file_name": previous.get("file_name"),
            "ai_model": ai_model,
            "temperature": temperature,
            "threshold": threshold,
        }
    except Exception:
        logger.exception("analysis_task_failed")
        raise

@celery_app.task(name="analysis.tasks.reporting_task", bind=True, rate_limit="2/m")
def reporting_task(
    self,
    previous: dict
):
    try:
        self.update_state(state="STARTED", meta={"stage": "reporting"})

        file_id = previous["file_id"]
        logger.debug("reporting_task_data", extra={"file_id": file_id})

        # loading data
        result = load_analysis(file_id, "full")
        report = {
            "file_id": file_id,
            "summary": result["summary"],
            "score": result["score"],
        }
        try:
            text = load_extracted_text(file_id)
            doc_len = len(text or "")
        except Exception:
            doc_len = 0
        _log_async_run(
            file_name=previous.get("file_name"),
            ai_model=previous.get("ai_model"),
            temperature=previous.get("temperature"),
            threshold=previous.get("threshold"),
            document_length=doc_len,
            result=report,
        )
        return report 
    except Exception as e:
        logger.exception("reporting_task_failed", extra={"file_id": file_id})
        raise 
