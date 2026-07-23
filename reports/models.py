from datetime import timedelta

from django.conf import settings
from django.db import models
from django.utils import timezone


class FloodReport(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name="reports")
    latitude = models.DecimalField( max_digits=9,decimal_places=6)
    longitude = models.DecimalField(max_digits=9,decimal_places=6)
    note = models.TextField(blank=True)
    confirmation_count = models.PositiveIntegerField(default=1)
    reported_at = models.DateTimeField(auto_now_add=True)
    last_confirmed = models.DateTimeField(null=True,blank=True)
    expires_at = models.DateTimeField()
    is_active = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if not self.pk:
            now = timezone.now()
            self.last_confirmed = now
            self.expires_at = now + timedelta(hours=2)

        super().save(*args, **kwargs)

    def __str__(self):
        return f"Report #{self.id}"


class Confirmation(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    report = models.ForeignKey(FloodReport,on_delete=models.CASCADE,related_name="confirmations")
    confirmed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "report"],
                name="unique_user_confirmation",
            )
        ]

    def __str__(self):
        return f"{self.user} confirmed Report #{self.report.id}"