from django.shortcuts import render
from documents.models import Document
from django.core.paginator import Paginator
from workflow.services import inbox_query


# Create your views here.


def index(request):
    department = request.user.profile.department  # or however you store it

    docs = inbox_query(department)

    paginator = Paginator(docs, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request, "workflow/inbox.html", {
        "page_obj": page_obj
    })
