from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    # path("inbox", views.inbox, name="inbox"),
    path("sent", views.sent_documents, name="sent_documents"),
    path("pending", views.pending_actions, name="pending_actions"),
    path(
        "documents/<int:document_id>/ack/",
        views.acknowledge_action,
        name="acknowledge_action"
    ),
    path(
        "documents/<int:document_id>/reject/",
        views.reject_action,
        name="reject_action"
    ),

    path(
        "documents/<int:document_id>/route/",
        views.route_action,
        name="route_action"
    ),
    path("api/departments/", views.departments_api, name="departments_api"),
    path("submit-route/", views.submit_route, name="submit_route"),
]
