from django import forms
from .ai_model_choices import AI_MODEL_PROVIDERS

class AnalysisForm(forms.Form):
    document_text = forms.CharField(
        required=False,
        label="Document Text",
        widget=forms.Textarea(
            attrs={
                "rows": 12,
                "placeholder": "Paste resume text or upload a PDF...",
            }
        ),
    )
    document_pdf = forms.FileField(required=False, label="Resume PDF")

    ai_model = forms.ChoiceField(
        choices=AI_MODEL_PROVIDERS,
        required=False,
        initial="llama-3.1-8b-instant",
        label="AI Model",
    )
    provider = forms.ChoiceField(
        choices=[
            ("groq", "Groq"),
            ("gemini", "Gemini"),
            ("openai", "OpenAI"),
        ],
        required=False,
        initial="groq",
        label="Model Provider",
    )
    temperature = forms.FloatField(
        required=False,
        min_value=0.0,
        max_value=1.0,
        initial=0.2,
        label="Temperature",
        widget=forms.NumberInput(attrs={"step": "0.1"}),
    )
    threshold = forms.IntegerField(
        required=False,
        min_value=0,
        max_value=100,
        initial=50,
        label="Threshold",
        widget=forms.NumberInput(attrs={"type": "range", "min": 0, "max": 100}),
    )

    ROLE_CHOICES = [
        ("founders_office", "Founder's Office"),
        ("sde", "SDE"),
        ("ds", "Data Science"),
        ("business", "Business"),
        ("product", "Product"),
    ]

    company_name = forms.CharField(
        required=False,
        label="Company Name",
        widget=forms.TextInput(attrs={"placeholder": "Acme Corp"}),
    )
    role = forms.ChoiceField(
        choices=ROLE_CHOICES,
        required=False,
        label="Role",
        
    )
    experience_level = forms.IntegerField(
        required=False,
        min_value=0,
        max_value=50,
        initial=3,
        label="Experience Level (Years)",
        widget=forms.NumberInput(attrs={"type": "range", "min": 0, "max": 50, "step": 1}),
    )
    job_description = forms.CharField(
        required=False,
        label="Job Description",
        widget=forms.Textarea(
            attrs={
                "rows": 4,
                "placeholder": "Role, key requirements, must-have skills...",
            }
        ),
    )

    jd_prompt = forms.CharField(
        required=False,
        label="Skills",
        initial="Examples: Python, Django, FastAPI, Redis, Celery, PostgreSQL",
        widget=forms.Textarea(
            attrs={
                "rows": 3,
                "placeholder": "List key skills...",
            }
        ),
    )


    def clean(self):
        cleaned = super().clean()
        text = (cleaned.get("document_text") or "").strip()
        pdf = cleaned.get("document_pdf")
        if not text and not pdf:
            raise forms.ValidationError("Provide document text or upload a PDF.")

        return cleaned
