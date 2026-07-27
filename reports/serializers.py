from django.utils import timezone

from .models import Confirmation, Confirmation, FloodReport
from rest_framework import serializers


# class FloodReportSerializer(serializers.ModelSerializer):
#     reported_by = serializers.CharField(source="user.full_name",read_only=True,)

#     class Meta:
#         model = FloodReport
#         fields = ("id","reported_by","latitude","longitude","note","confirmation_count","reported_at","last_confirmed","expires_at","status","is_active")
#         read_only_fields = ("confirmation_count","reported_at","last_confirmed","expires_at","status","is_active")


class FloodReportSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source="user.full_name", read_only=True)
    minutes_until_expiry = serializers.SerializerMethodField()
    has_confirmed = serializers.SerializerMethodField()

    class Meta:
        model = FloodReport
        fields = ("id","full_name","latitude","longitude","note","status","confirmation_count","reported_at","last_confirmed","expires_at","minutes_until_expiry","has_confirmed",)
        read_only_fields = ("confirmation_count","reported_at","last_confirmed","expires_at","status","is_active", "minutes_until_expiry","has_confirmed",)


    def get_minutes_until_expiry(self, obj):
        remaining = obj.expires_at - timezone.now()

        minutes = int(remaining.total_seconds() / 60)
    
        return max(minutes, 0)

    def get_has_confirmed(self, obj):
        request = self.context.get("request")

        if request is None:
            return False

        if request.user.is_anonymous:
            return False

        return Confirmation.objects.filter(
            user=request.user,
            report=obj,
        ).exists()