from django.shortcuts import render
from documents.models import Document
from django.core.paginator import Paginator
from workflow.services import inbox_query, sent_query, pending_query


# Create your views here.


def index(request):
    department = request.user.profile.department  # or however you store it

    docs = inbox_query(department)

    paginator = Paginator(docs, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request, "workflow/inbox.html", {
        "page_obj": page_obj,
        "page_obj": page_obj,

        # table behavior
        "show_actions": True,

        # workflow capabilities
        "allowed_actions": [
            "route",
        ]
    })


def sent_documents(request):
    # SENT = documents where my department is the latest actor in routing history
    department = request.user.profile.department

    docs = sent_query(department)

    paginator = Paginator(docs, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request, "workflow/sent.html", {
        "page_obj": page_obj,
        "page_obj": page_obj,

        # table behavior
        "show_actions": False,

    })


def pending_actions(request):
    department = request.user.profile.department

    docs = pending_query(department)

    paginator = Paginator(docs, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request, "workflow/pending.html", {
        "page_obj": page_obj,

        # table behavior
        "show_actions": True,

        # workflow capabilities
        "allowed_actions": [
            "ack",
            "reject",
            "route",
        ]

    })
