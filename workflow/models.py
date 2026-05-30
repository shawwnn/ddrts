from django.db import models
from accounts.models import Department
from documents.models import Document
from django.contrib.auth.models import User


# Create your models here.
class RoutingHistory(models.Model):
    ACTION_CHOICES = [
        ('route', 'Route'),
        ('ack', 'Acknowledge'),
        ('reject', 'Reject/No Documents Received'),
    ]

    document = models.ForeignKey(Document, on_delete=models.CASCADE)

    from_department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        null=True,
        related_name='from_routes'
    )

    to_department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        null=True,
        related_name='to_routes'
    )

    action = models.CharField(max_length=20, choices=ACTION_CHOICES)

    performed_by = models.ForeignKey(User, on_delete=models.CASCADE)

    remarks = models.TextField(blank=True, null=True)

    routed_at = models.DateTimeField(auto_now_add=True)
