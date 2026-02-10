from django.conf import settings
from django.urls import path
from . import views
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

app_name = "ui"

urlpatterns = [
    path("", views.index, name="index"),
    path("analytics/", views.analytics, name="analytics"),
    path("technical-docs/", views.technical_docs, name="technical_docs"),
]

if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
