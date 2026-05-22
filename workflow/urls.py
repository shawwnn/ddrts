from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    # path("inbox", views.inbox, name="inbox"),
    path("sent", views.sent_documents, name="sent_documents")
]
