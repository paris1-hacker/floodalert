from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from django.contrib.auth.tokens import default_token_generator


class EmailService:

    @staticmethod
    def send_verification_email(user):

        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)

        verification_url = (
            f"{settings.FRONTEND_URL}/verify-email"
            f"?uid={uid}&token={token}"
        )

        html_message = render_to_string(
            "emails/verify_email.html",
            {
                "user": user,
                "verification_url": verification_url,
            },
        )

        email = EmailMultiAlternatives(
            subject="Verify your FloodAlert account",
            body="Please verify your account.",
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[user.email],
        )

        email.attach_alternative(html_message, "text/html")
        email.send()