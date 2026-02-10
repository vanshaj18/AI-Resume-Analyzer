from django.db import models


class AnalysisRun(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    source = models.CharField(max_length=16, default="text")
    file_name = models.CharField(max_length=255, blank=True)
    ai_model = models.CharField(max_length=64, default="llama-3.1-8b-instant")
    temperature = models.FloatField(default=0.2)
    threshold = models.IntegerField(default=50)
    has_pdf = models.BooleanField(default=False)
    document_length = models.IntegerField(default=0)
    result_json = models.TextField(blank=True)

    class Meta:
        ordering = ["-created_at"]
