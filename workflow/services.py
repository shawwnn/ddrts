from django.db import transaction
from documents.models import Document
from workflow.models import RoutingHistory
from django.contrib.auth.models import User
from django.db.models import OuterRef, Subquery

def route_document(document_id, from_dept, to_dept, user, remarks=""):
    with transaction.atomic():

        doc = Document.objects.select_for_update().get(id=document_id)

        # SAFETY CHECK 1: ownership
        if doc.current_department != from_dept:
            raise Exception("Unauthorized routing attempt")

        # SAFETY CHECK 2: cannot route to same department
        if from_dept == to_dept:
            raise Exception("Cannot route to same department")

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
    # latest_route = RoutingHistory.objects.filter(
    #     document=OuterRef('pk')
    # ).order_by('-timestamp')

    # docs = Document.objects.annotate(
    #     last_action=Subquery(latest_route.values('action')[:1]),
    #     last_to=Subquery(latest_route.values('to_department')[:1])
    #     ).filter(
    #     last_to=department,
    #     last_action='route'
    # )

    # return docs

    return Document.objects.filter(
        current_department=department
    )