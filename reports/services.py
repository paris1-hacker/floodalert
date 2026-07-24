from datetime import timedelta

from django.utils import timezone

from .models import FloodReport


def refresh_report_statuses():
    """
    Update all active flood reports based on the time
    since they were last confirmed.
    """

    now = timezone.now()

    reports = FloodReport.objects.filter(is_active=True)

    for report in reports:
        elapsed = now - report.last_confirmed

        if elapsed >= timedelta(hours=4):
            report.status = "expired"
            report.is_active = False

        elif elapsed >= timedelta(hours=2):
            report.status = "warning"

        else:
            report.status = "live"

        report.save(update_fields=["status", "is_active"])