from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings

def send_expense_email(subject, template_name, context, recipient_list):
    html_message = render_to_string(template_name, context)
    plain_message = render_to_string(template_name.replace('.html', '.txt'), context)
    send_mail(subject, plain_message, settings.DEFAULT_FROM_EMAIL, recipient_list, html_message=html_message, fail_silently=False)
