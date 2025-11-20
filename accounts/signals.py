from django.contrib.auth.signals import user_logged_in, user_login_failed
from django.dispatch import receiver
from .models import LoginAttempt, Account


def _get_client_ip(request):
    if not request:
        return None
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def _trim_user_agent(request):
    if not request:
        return ''
    ua = request.META.get('HTTP_USER_AGENT', '')
    return ua[:255]


@receiver(user_logged_in)
def log_successful_login(sender, request, user, **kwargs):
    LoginAttempt.objects.create(
        user=user,
        email=user.email,
        ip_address=_get_client_ip(request),
        user_agent=_trim_user_agent(request),
        success=True,
    )


@receiver(user_login_failed)
def log_failed_login(sender, credentials, request, **kwargs):
    email = ''
    if credentials:
        email = credentials.get('username') or credentials.get('email') or ''
    LoginAttempt.objects.create(
        user=None,
        email=email,
        ip_address=_get_client_ip(request),
        user_agent=_trim_user_agent(request),
        success=False,
    )

