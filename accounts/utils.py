from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode


def detect_user(user):
    if user.role == 1:
        redirect_url = 'vendor_dashboard'
        return redirect_url
    elif user.role == 2:
        redirect_url = 'customer_dashboard'
        return redirect_url
    elif user.role is None and user.is_superadmin:
        redirect_url = '/admin'
        return redirect_url


def send_verification_email(request, user, mail_subject, email_template):
    from_email = settings.DEFAULT_FROM_EMAIL
    current_site = get_current_site(request)
    message = render_to_string(email_template, {
        'user': user,
        'domain': current_site,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': default_token_generator.make_token(user),
    })
    to_email = user.email
    mail = EmailMessage(mail_subject, message, from_email, to=[to_email])
    mail.send()


def send_notification(mail_subject, email_template, context):
    from_email = settings.DEFAULT_FROM_EMAIL
    message = render_to_string(email_template, context)
    to_email = context['to_email']
    mail = EmailMessage(mail_subject, message, from_email, to=[to_email])
    mail.send()
