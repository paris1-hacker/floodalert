from .models import FloodReport
from rest_framework import serializers


class FloodReportSerializer(serializers.ModelSerializer):
    reported_by = serializers.CharField(source="user.full_name",read_only=True,)

    class Meta:
        model = FloodReport
        fields = ("id","reported_by","latitude","longitude","note","confirmation_count","reported_at","last_confirmed","expires_at","is_active")
        read_only_fields = ("confirmation_count","reported_at","last_confirmed","expires_at","is_active")

