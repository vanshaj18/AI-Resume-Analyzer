import json
import os
import tempfile

from django.shortcuts import render, redirect
from django.utils import timezone

from .forms import AnalysisForm
from .ai_model_choices import AI_MODEL_PROVIDERS
from .models import AnalysisRun
from .services import run_full_analysis, backend_url
from .pdf_utils import pdf_reader

try:
    from utils.pyresparser.resume_parser import ResumeParser
except Exception:
    ResumeParser = None


def _extract_from_pdf(uploaded_file):
    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            for chunk in uploaded_file.chunks():
                tmp.write(chunk)
            tmp_path = tmp.name

        resume_text = pdf_reader(tmp_path)
        resume_data = None
        if ResumeParser is not None:
            resume_data = ResumeParser(tmp_path).get_extracted_data()

        return resume_text, resume_data
    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.remove(tmp_path)


def index(request):
    result = request.session.pop("ui_result", None)
    error = request.session.pop("ui_error", None)
    resume_data = request.session.pop("ui_resume_data", None)

    if request.method == "POST":
        form = AnalysisForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                document_text = (form.cleaned_data.get("document_text") or "").strip()
                pdf_file = form.cleaned_data.get("document_pdf")

                if pdf_file:
                    try:
                        pdf_text, resume_data = _extract_from_pdf(pdf_file)
                        if not document_text:
                            document_text = (pdf_text or "").strip()
                    except Exception as exc:
                        error = f"Failed to parse PDF: {exc}"

                if not error:
                    criteria = {
                        "company_name": (form.cleaned_data.get("company_name") or "").strip() or None,
                        "role": form.cleaned_data.get("role") or None,
                        "experience_level": form.cleaned_data.get("experience_level"),
                        "job_description": (form.cleaned_data.get("job_description") or "").strip() or None,
                    }
                    result = run_full_analysis(
                        document_text,
                        ai_model=form.cleaned_data.get("ai_model"),
                        temperature=form.cleaned_data.get("temperature") or 0.2,
                        threshold=form.cleaned_data.get("threshold") or 70,
                        criteria=criteria,
                        jd_prompt=(form.cleaned_data.get("jd_prompt") or "").strip() or None,
                    )

                    AnalysisRun.objects.create(
                        created_at=timezone.now(),
                        source="pdf" if pdf_file else "text",
                        file_name=pdf_file.name if pdf_file else "text",
                        ai_model=form.cleaned_data.get("ai_model") or "llama-3.1-8b-instant",
                        temperature=form.cleaned_data.get("temperature") or 0.2,
                        threshold=form.cleaned_data.get("threshold") or 50,
                        has_pdf=bool(pdf_file),
                        document_length=len(document_text),
                        result_json=json.dumps(result),
                    )
            except Exception as exc:
                error = str(exc)
        else:
            error = "Invalid input. Please check the form and try again."

        request.session["ui_result"] = result
        request.session["ui_error"] = error
        request.session["ui_resume_data"] = resume_data
        return redirect("ui:index")

    form = AnalysisForm()
    return render(
        request,
        "ui/index.html",
        {
            "form": form,
            "result": result,
            "error": error,
            "resume_data": resume_data,
            "backend_url": backend_url,
            "ai_model_providers": AI_MODEL_PROVIDERS,
        },
    )


def analytics(request):
    runs = AnalysisRun.objects.all()[:100]
    runs_data = []
    for run in runs:
        summary = ""
        score = ""
        provider = ""
        try:
            payload = json.loads(run.result_json or "{}")
            summary = payload.get("summary", "")
            score = payload.get("score", "")
        except Exception:
            summary = ""
            score = ""
        model_name = run.ai_model or ""
        if model_name.startswith("gemini"):
            provider = "gemini"
        elif model_name.startswith("openai/"):
            provider = "openai"
        else:
            provider = "groq"
        runs_data.append(
            {
                "created_at": run.created_at,
                "source": run.source,
                "file_name": run.file_name,
                "ai_model": run.ai_model,
                "provider": provider,
                "temperature": run.temperature,
                "threshold": run.threshold,
                "document_length": run.document_length,
                "summary": summary,
                "score": score,
            }
        )
    return render(request, "ui/analytics.html", {"runs": runs_data})


def technical_docs(request):
    return render(request, "ui/technical_docs.html")
