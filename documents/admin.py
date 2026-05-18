from django.contrib import admin
from documents.models import Document, DocumentFile

# Register your models here.
admin.site.register(Document)
admin.site.register(DocumentFile)