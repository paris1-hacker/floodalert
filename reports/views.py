from django.conf import settings
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
from .services import refresh_report_statuses
from .utils import is_within_tolerance, distance_in_meters
from drf_spectacular.utils import (
    extend_schema,
    OpenApiParameter,
    OpenApiTypes,
)


# def get_queryset(self):
#     FloodReport.objects.filter(
#         is_active=True,
#         expires_at__lte=timezone.now(),
#     ).update(is_active=False)

#     return (
#         FloodReport.objects.filter(is_active=True)
#         .select_related("user")
#         .order_by("-last_confirmed", "-reported_at")
#     )

@extend_schema(
    parameters=[
        OpenApiParameter(
            name="status",
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description="Filter reports by status. Allowed values: live, warning",
        ),
    ]
)
class FloodReportListCreateAPIView(ListCreateAPIView):
    serializer_class = FloodReportSerializer

    def get_permissions(self):
        if self.request.method == "GET":
            return [AllowAny()]
        return [IsAuthenticated()]

    def get_queryset(self):
        refresh_report_statuses()

        queryset = (
            FloodReport.objects.filter(is_active=True)
            .select_related("user")
            .order_by("-last_confirmed", "-reported_at")
        )
        
        status_filter = self.request.query_params.get("status")

        if status_filter:
            valid_statuses = ["live", "warning"]

            if status_filter not in valid_statuses:
                return FloodReport.objects.none()

            queryset = queryset.filter(status=status_filter)
        return queryset

    def list(self, request, *args, **kwargs):
        serializer = self.get_serializer(self.get_queryset(),many=True, context={"request": request})

        return Response(
            {
                "success": True,
                "message": "Flood reports retrieved successfully.",
                "data": serializer.data
            }
        )

    def create(self, request, *args, **kwargs):
        latitude = request.data.get("latitude")
        longitude = request.data.get("longitude")

        if latitude is None or longitude is None:
            return Response(
                {
                    "success": False,
                    "message": "Latitude and longitude are required.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        active_reports = FloodReport.objects.filter(is_active=True)

        for report in active_reports:
            distance = distance_in_meters(
                latitude,
                longitude,
                report.latitude,
                report.longitude,
            )

            if is_within_tolerance(
                latitude,
                longitude,
                report.latitude,
                report.longitude,
            ):
                return Response(
                    {
                        "success": False,
                        "message": "An active flood report already exists nearby. Please confirm it instead.",
                        "data": {
                            "report_id": report.id,
                            "distance_in_meters": round(distance, 2),
                        },
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        flood_report = serializer.save(user=request.user)

        return Response(
            {
                "success": True,
                "message": "Flood report created successfully.",
                "data": FloodReportSerializer(flood_report, context={"request": request}).data
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
        # Refresh report statuses before retrieving
        refresh_report_statuses()

        return (
            FloodReport.objects.filter(is_active=True)
            .select_related("user")
        )

    def retrieve(self, request, *args, **kwargs):
        
        report = self.get_object()

        return Response(
            {
                "success": True,
                "message": "Flood report retrieved successfully.",
                "data": FloodReportSerializer(report, context={"request": request}).data
                # "data": FloodReportSerializer(report).data,
            }
        )

class ConfirmFloodReportAPIView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    

    @transaction.atomic    
    def post(self, request, pk):
        # Refresh statuses before allowing confirmation
        refresh_report_statuses()

        report = get_object_or_404(FloodReport,pk=pk,is_active=True)

        # Prevent duplicate confirmations
        if Confirmation.objects.filter(
            user=request.user,
            report=report,
        ).exists():
            return Response(
                {
                    "success": False,
                    "message": "You have already confirmed this report.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        Confirmation.objects.create(
            user=request.user,
            report=report,
        )

        now = timezone.now()
        report.confirmation_count += 1
        report.last_confirmed = now
        report.expires_at = now + timedelta(hours=2)
        report.status = "live"
        report.is_active = True

        report.save(
            update_fields=[
                "confirmation_count",
                "last_confirmed",
                "expires_at",
                "status",
                "is_active",
            ]
        )
        
        return Response(
            {
                "success": True,
                "message": "Flood report confirmed successfully.",
                "data": FloodReportSerializer(report, context={"request": request}).data
            }
        )

# class FloodReportRetrieveAPIView(RetrieveAPIView):
#     serializer_class = FloodReportSerializer
    
#     def get_permissions(self):
#             if self.request.method == "GET":
#                 return [AllowAny()]
#             return [IsAuthenticated()]
    

#     def get_queryset(self):
#         FloodReport.objects.filter(is_active=True,expires_at__lte=timezone.now(),).update(is_active=False)

#         return (
#             FloodReport.objects.filter(is_active=True).select_related("user")
#     )


#     def retrieve(self, request, *args, **kwargs):
#         report = self.get_object()

#         return Response(
#             {
#                 "success": True,
#                 "message": "Flood report retrieved successfully.",
#                 "data": FloodReportSerializer(report).data,
#             }
#         )



# class ConfirmFloodReportAPIView(GenericAPIView):
#     permission_classes = [IsAuthenticated]

#     def post(self, request, pk):

#         # First deactivate expired reports
#         FloodReport.objects.filter(is_active=True,expires_at__lte=timezone.now(),).update(is_active=False)

#         # Now try to get the report
#         report = get_object_or_404(FloodReport,pk=pk,is_active=True,)

#         # Prevent duplicate confirmations
#         if Confirmation.objects.filter(user=request.user,report=report,
#         ).exists():
#             return Response(
#                 {
#                     "success": False,
#                     "message": "You have already confirmed this report."
#                 },
#                 status=status.HTTP_400_BAD_REQUEST,
#             )

#         Confirmation.objects.create(user=request.user,report=report)

#         now = timezone.now()

#         report.confirmation_count += 1
#         report.last_confirmed = timezone.now()
#         report.expires_at = timezone.now() + timedelta(hours=2)

#         report.status = "live"
#         report.is_active = True

#         report.save()

#         return Response(
#             {
#                 "success": True,
#                 "message": "Flood report confirmed successfully.",
#                 "data": FloodReportSerializer(report).data,
#             }
#         )




class NearbyFloodReportsAPIView(GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = FloodReportSerializer

    def get(self, request):
        refresh_report_statuses()

        latitude = request.query_params.get("latitude")
        longitude = request.query_params.get("longitude")

        if not latitude or not longitude:
            return Response(
                {
                    "success": False,
                    "message": "Latitude and longitude are required.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        radius = request.query_params.get(
            "radius",
            settings.DEFAULT_NEARBY_RADIUS_METERS,
        )

        try:
            radius = float(radius)
        except ValueError:
            return Response(
                {
                    "success": False,
                    "message": "Radius must be a valid number.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        reports = (
            FloodReport.objects.filter(is_active=True)
            .select_related("user")
            .order_by("-last_confirmed")
        )

        nearby_reports = []

        for report in reports:
            distance = distance_in_meters(
                latitude,
                longitude,
                report.latitude,
                report.longitude,
            )

            if distance <= radius:
                data = FloodReportSerializer(report).data
                data["distance_in_meters"] = round(distance, 2)
                nearby_reports.append(data)

        return Response(
            {
                "success": True,
                "message": "Nearby flood reports retrieved successfully.",
                "count": len(nearby_reports),
                "data": nearby_reports,
            }
        )