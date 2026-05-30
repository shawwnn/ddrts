from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.shortcuts import render
from documents.models import Document
from accounts.models import Department
from django.core.paginator import Paginator
from workflow.services import inbox_query, sent_query, pending_query, submit_route_document
from workflow.services import (
    acknowledge_document,
    reject_document,
    route_document
)

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


@require_POST
def acknowledge_action(request, document_id):
    try:
        acknowledge_document(document_id, user=request.user)

        return JsonResponse({
            "success": True,
            "message": "Document acknowledged successfully."
        })
    except Exception as e:
        return JsonResponse({
            "success": False,
            "error": str(e)
        },
            status=400)


@require_POST
def reject_action(request, document_id):
    try:
        reject_document(document_id, user=request.user)

        return JsonResponse({
            "success": True,
            "message": "Document rejected successfully."
        })
    except Exception as e:
        return JsonResponse({
            "success": False,
            "error": str(e)
        },
            status=400)


@require_POST
def route_action(request, document_id):
    try:
        to_department_id = request.POST.get("to_department")

        route_document(
            document_id=document_id,
            from_dept=request.user.profile.department,
            to_dept_id=to_department_id,
            user=request.user
        )

        return JsonResponse({
            "success": True,
            "action": "route",
            "message": "Document routed successfully."
        })

    except Exception as e:
        return JsonResponse({
            "success": False,
            "message": str(e)
        }, status=400)


def departments_api(request):
    departments = Department.objects.all().values("id", "name")

    return JsonResponse(list(departments), safe=False)


@require_POST
def submit_route(request):
    result = submit_route_document(
        document_id=request.POST.get("document_id"),
        to_department_id=request.POST.get("to_department_id"),
        remarks=request.POST.get("remarks"),
        user=request.user,
    )

    return JsonResponse(result)
