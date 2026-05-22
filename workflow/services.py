from django.db.models import OuterRef, Subquery, Q
from django.db import transaction
from documents.models import Document
from workflow.models import RoutingHistory
from django.contrib.auth.models import User
from django.db.models import OuterRef, Subquery
from django.db.models.functions import Coalesce

# def create_and_route_document(user, title, from_dept, to_dept):
#     doc = Document.objects.create(
#         title=title,
#         created_by=user,
#         current_department=from_dept
#     )

#     RoutingHistory.objects.create(
#         document=doc,
#         from_department=from_dept,
#         to_department=to_dept,
#         action="route",
#         performed_by=user,
#         remarks="FAA"
#     )

#     doc.current_department = to_dept
#     doc.save()

#     return doc


def route_document(document_id, from_dept, to_dept, user, remarks=""):
    with transaction.atomic():

        doc = Document.objects.select_for_update().get(id=document_id)

        # SAFETY CHECK 1: ownership
        # if doc.current_department != from_dept:
        #     raise Exception("Unauthorized routing attempt")

        # SAFETY CHECK 2: cannot route to same department
        # if from_dept == to_dept:
        #     raise Exception("Cannot route to same department")

        RoutingHistory.objects.create(
            document=doc,
            from_department=from_dept,
            to_department=to_dept,
            action='route',
            performed_by=user,
            remarks=remarks
        )

        return doc


def acknowledge_document(document_id, user, remarks=""):
    with transaction.atomic():

        doc = Document.objects.select_for_update().get(id=document_id)

        last_route = RoutingHistory.objects.filter(
            document=doc
        ).order_by('-id').first()

        # SAFETY CHECK 1: must exist
        if not last_route:
            raise Exception("No routing history found")

        # SAFETY CHECK 2: must be route
        if last_route.action != 'route':
            raise Exception("Only routed documents can be acknowledged")

        # SAFETY CHECK 3: must be for this department
        if last_route.to_department != user.profile.department:
            raise Exception("Document not assigned to this department")

        from_dept = doc.current_department
        to_dept = user.profile.department

        RoutingHistory.objects.create(
            document=doc,
            from_department=from_dept,
            to_department=to_dept,
            action='ack',
            performed_by=user,
            remarks=remarks
        )

        # ACTUAL TRANSFER
        doc.current_department = to_dept
        doc.save()

        return doc


def reject_document(document_id, user, remarks="No documents received"):
    with transaction.atomic():

        doc = Document.objects.select_for_update().get(id=document_id)

        last_route = RoutingHistory.objects.filter(
            document=doc
        ).order_by('-id').first()

        # SAFETY CHECK 1: must have history
        if not last_route:
            raise Exception("No routing history found")

        # SAFETY CHECK 2: must be routed
        if last_route.action != 'route':
            raise Exception("Only routed documents can be rejected")

        # SAFETY CHECK 3: must be for this department
        if last_route.to_department != user.profile.department:
            raise Exception("Document not routed to this department")

        # SAFETY CHECK 4: cannot reject already processed docs
        if doc.current_department != user.profile.department:
            raise Exception("Document already processed")

        RoutingHistory.objects.create(
            document=doc,
            from_department=doc.current_department,
            to_department=user.profile.department,
            action='reject',
            performed_by=user,
            remarks=remarks
        )

        return doc


def inbox_query(department):
    """
    📥 Inbox Query:
    Fetch documents currently assigned to a department
    + attach latest routing history (computed fields)
    """
    latest_route = RoutingHistory.objects.filter(
        document=OuterRef('pk')
    ).order_by('-routed_at')

    docs = Document.objects.filter(
        current_department=department
    ).annotate(

        # 📌 Last action taken (route / ack / reject)
        last_action=Subquery(
            latest_route.values('action')[:1]
        ),

        # 📌 Department where it came from last
        last_from_department=Coalesce(
            Subquery(latest_route.values('from_department__name')[:1]),
            'creator_department__name'   # fallback ONLY if no routing exists
        ),

        # 📌 Department where it is going next
        last_to_department=Subquery(
            latest_route.values('to_department__name')[:1]
        ),

        # 📌 Last activity timestamp
        last_activity_time=Coalesce(
            Subquery(latest_route.values('routed_at')[:1]),
            'created_at'   # fallback ONLY if no routing exists
        ),
    )

    return docs


def sent_query(department):
    """
    📤 Sent Query:
    Fetch documents where the latest routing action
    came FROM the current user's department
    """

    latest_route = RoutingHistory.objects.filter(
        document=OuterRef('pk')
    ).order_by('-routed_at')

    docs = Document.objects.annotate(

        last_action=Subquery(
            latest_route.values('action')[:1]
        ),

        last_from_department=Subquery(
            latest_route.values('from_department__name')[:1]
        ),

        last_to_department=Subquery(
            latest_route.values('to_department__name')[:1]
        ),

        last_activity_time=Coalesce(
            Subquery(latest_route.values('routed_at')[:1]),
            'created_at'
        ),
    ).filter(
        last_from_department=department.name
    )

    return docs
