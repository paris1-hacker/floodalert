from datetime import timedelta
from django.utils import timezone
from rest_framework import status
from rest_framework.generics import ListCreateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from .models import FloodReport, Confirmation
from .serializers import FloodReportSerializer
from rest_framework.generics import RetrieveAPIView, GenericAPIView
from django.shortcuts import get_object_or_404
from django.db import transaction


class FloodReportListCreateAPIView(ListCreateAPIView):
    serializer_class = FloodReportSerializer
    
    def get_permissions(self):
        if self.request.method == "GET":
            return [AllowAny()]
        return [IsAuthenticated()]


    def get_queryset(self):
        # Mark expired reports as inactive
        FloodReport.objects.filter(is_active=True,expires_at__lte=timezone.now(),
        ).update(is_active=False)

        return (
            FloodReport.objects.filter(is_active=True)
            .select_related("user")
            .order_by("-last_confirmed", "-reported_at")
        )




    def list(self, request, *args, **kwargs):
        serializer = self.get_serializer(self.get_queryset(), many=True)

        return Response(
            {
                "success": True,
                "message": "Flood reports retrieved successfully.",
                "data": serializer.data,
            }
        )

    def create(self, request, *args, **kwargs):
        latitude = request.data.get("latitude")
        longitude = request.data.get("longitude")

        duplicate = FloodReport.objects.filter(is_active=True,latitude=latitude,longitude=longitude,
        ).first()

        if duplicate:
            return Response(
                {
                    "success": False,
                    "message": "An active flood report already exists for this location. Please confirm it instead.",
                    "data": {
                        "report_id": duplicate.id,
                    },
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        report = serializer.save(user=request.user)

        return Response(
            {
                "success": True,
                "message": "Flood report created successfully.",
                "data": FloodReportSerializer(report).data,
            },
            status=status.HTTP_201_CREATED,
        )

class FloodReportRetrieveAPIView(RetrieveAPIView):
    serializer_class = FloodReportSerializer
    
    def get_permissions(self):
            if self.request.method == "GET":
                return [AllowAny()]
            return [IsAuthenticated()]
    

    def get_queryset(self):
        FloodReport.objects.filter(is_active=True,expires_at__lte=timezone.now(),).update(is_active=False)

        return (
            FloodReport.objects.filter(is_active=True).select_related("user")
    )


    def retrieve(self, request, *args, **kwargs):
        report = self.get_object()

        return Response(
            {
                "success": True,
                "message": "Flood report retrieved successfully.",
                "data": FloodReportSerializer(report).data,
            }
        )



class ConfirmFloodReportAPIView(GenericAPIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):

        # First deactivate expired reports
        FloodReport.objects.filter(is_active=True,expires_at__lte=timezone.now(),).update(is_active=False)

        # Now try to get the report
        report = get_object_or_404(FloodReport,pk=pk,is_active=True,)

        # Prevent duplicate confirmations
        if Confirmation.objects.filter(user=request.user,report=report,
        ).exists():
            return Response(
                {
                    "success": False,
                    "message": "You have already confirmed this report."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        Confirmation.objects.create(user=request.user,report=report)

        now = timezone.now()

        report.confirmation_count += 1
        report.last_confirmed = now
        report.expires_at = now + timedelta(hours=2)
        report.save()

        return Response(
            {
                "success": True,
                "message": "Flood report confirmed successfully.",
                "data": FloodReportSerializer(report).data,
            }
        )
