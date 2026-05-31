# documents/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path(
        "<int:document_id>/",
        views.document_detail,
        name="document_detail"
    ),
]
