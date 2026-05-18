from django.db import models
from django.contrib.auth.models import User
from accounts.models import Department

# Create your models here.
class Document(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('archived', 'Archived'),
    ]

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    current_department = models.ForeignKey(Department, on_delete=models.PROTECT)
    creator_department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_documents'
    )


    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class DocumentFile(models.Model):
    document = models.ForeignKey(Document, on_delete=models.CASCADE)
    file = models.FileField(upload_to='documents/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

