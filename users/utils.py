"""
Utility functions for user management
"""
from datetime import timedelta
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse
from django.template.loader import render_to_string
from django.core import signing
from django.utils.crypto import get_random_string
import logging

logger = logging.getLogger(__name__)


def generate_signed_token(user, expires_in_seconds=86400):
    """Generate a signed token containing user PK and a random nonce."""
    signer = signing.TimestampSigner()
    payload = f"{user.pk}:{get_random_string(12)}"
    signed = signer.sign(payload)
    return signed


def send_password_reset_email(user, request):
    """
    Send password reset link to user using a signed token (no DB fields required).
    """
    token = generate_signed_token(user)

    reset_url = request.build_absolute_uri(
        reverse('users:password_reset_confirm', kwargs={'token': token})
    )

    context = {
        'user': user,
        'reset_url': reset_url,
    }

    subject = 'Reset your password - Zorpido Restaurant'
    html_message = render_to_string('users/email/reset_password.html', context)
    plain_message = render_to_string('users/email/reset_password.txt', context)

    from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', None) or settings.EMAIL_HOST_USER

    try:
        send_mail(
            subject,
            plain_message,
            from_email,
            [user.email],
            html_message=html_message,
            fail_silently=False,
        )
        logger.info('Sent password reset email to %s', user.email)
    except Exception as exc:
        logger.exception('Failed sending password reset email to %s: %s', user.email, exc)

def send_password_reset_email(user, request):
    """
    Send password reset link to user
    """
    token = generate_signed_token(user)
    user.email_verification_token = token
    user.token_expiry = timezone.now() + timedelta(hours=24)
    user.save()

    reset_url = request.build_absolute_uri(
        reverse('users:password_reset_confirm', kwargs={'token': token})
    )

    context = {
        'user': user,
        'reset_url': reset_url,
    }

    subject = 'Reset your password - Zorpido Restaurant'
    html_message = render_to_string('users/email/reset_password.html', context)
    plain_message = render_to_string('users/email/reset_password.txt', context)

    try:
        send_mail(
            subject,
            plain_message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            html_message=html_message,
            fail_silently=False,
        )
        logger.info('Sent password reset email to %s', user.email)
    except Exception as exc:
        logger.exception('Failed sending password reset email to %s: %s', user.email, exc)

def verify_token(token):
    """
    Verify a token and return the associated user if valid
    Returns (user, error_message) tuple
    """
    from .models import User
    signer = signing.TimestampSigner()
    try:
        unsigned = signer.unsign(token, max_age=86400)
    except signing.SignatureExpired:
        return None, 'Token has expired'
    except signing.BadSignature:
        return None, 'Invalid token'

    # unsigned payload is 'user_pk:nonce'
    try:
        user_pk = int(unsigned.split(':', 1)[0])
    except Exception:
        return None, 'Invalid token payload'

    try:
        user = User.objects.get(pk=user_pk)
    except User.DoesNotExist:
        return None, 'User not found for token'

    return user, None