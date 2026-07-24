from django.urls import path
from .views import NearbyFloodReportsAPIView
from .views import (
    ConfirmFloodReportAPIView,
    FloodReportListCreateAPIView,
    FloodReportRetrieveAPIView,
)

urlpatterns = [
    path("",FloodReportListCreateAPIView.as_view(),name="report-list-create",),
    path("<int:pk>/",FloodReportRetrieveAPIView.as_view(),name="report-detail"),
    path("<int:pk>/confirm/",ConfirmFloodReportAPIView.as_view(),name="confirm-report"),
    path("reports/nearby/",NearbyFloodReportsAPIView.as_view(),name="nearby-reports"),
]

