from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings

def send_email(subject, template_name, context, recipient_list):
    html_message = render_to_string(template_name, context)
    plain_message = strip_tags(html_message)
    from_email = settings.DEFAULT_FROM_EMAIL

    send_mail(subject, plain_message, from_email, recipient_list, html_message=html_message)
