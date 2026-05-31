from django.shortcuts import render

from documents.models import Document

from django.shortcuts import get_object_or_404
from workflow.models import RoutingHistory

# Create your views here.


def document_detail(request, document_id):
    doc = get_object_or_404(Document, id=document_id)

    history = RoutingHistory.objects.filter(
        document=doc
    ).select_related(
        "from_department",
        "to_department",
        "performed_by"
    ).order_by("-routed_at")

    return render(request, "documents/document_detail.html", {
        "doc": doc,
        "history": history,
    })
