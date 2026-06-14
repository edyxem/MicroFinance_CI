from django.urls import path
from .views import ExportCreditsCSVView, ExportRapportPDFView

urlpatterns = [
    path('credits/csv/',    ExportCreditsCSVView.as_view(),     name='export-credits-csv'),
    path('rapport/pdf/',    ExportRapportPDFView.as_view(),     name='export-rapport-pdf'),
]