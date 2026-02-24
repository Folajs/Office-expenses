from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.contrib.auth import get_user_model
from .models import Expense

User = get_user_model()


@receiver(post_save, sender=Expense)
def notify_on_expense_submission(sender, instance, created, **kwargs):
    if not created:
        return

    recipients = []

    department = instance.department

    # Get Department Head by role instead of department.head field
    head = User.objects.filter(
        department=department,
        role="DEPARTMENT_HEAD"
    ).first()

    if head:
        recipients.append(head.email)

    # Get Finance users globally (or filter by department if required)
    finance_users = User.objects.filter(role="FINANCE")

    recipients.extend([u.email for u in finance_users])

    if recipients:
        send_mail(
            subject="New Expense Submitted",
            message=f"Expense has been submitted for review.",
            from_email=None,
            recipient_list=recipients,
            fail_silently=True,
        )
