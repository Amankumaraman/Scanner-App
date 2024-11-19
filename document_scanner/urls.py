from django.urls import path
from .views import index, scan_document

urlpatterns = [
    path('', index, name='index'),
    path('scan/', scan_document, name='scan_document'),
]
