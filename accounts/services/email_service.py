import resend

from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode


resend.api_key = settings.RESEND_API_KEY


class EmailService:
    """
    Handles all outgoing emails.
    """

    @staticmethod
    def send_verification_email(user):
        """
        Send email verification link.
        """

        uid = urlsafe_base64_encode(
            force_bytes(user.pk)
        )

        token = default_token_generator.make_token(user)

        verification_url = (
            f"{settings.FRONTEND_URL}"
            f"/verify-email"
            f"?uid={uid}&token={token}"
        )

        html = render_to_string(
            "emails/verify_email.html",
            {
                "user": user,
                "verification_url": verification_url,
            },
        )

        resend.Emails.send(
            {
                "from": settings.DEFAULT_FROM_EMAIL,
                "to": [user.email],
                "subject": "Verify your FloodAlert account",
                "html": html,
            }
        )