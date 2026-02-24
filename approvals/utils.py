from django.core.mail import send_mail
from django.conf import settings
from users.models import User


def send_rejection_email(expense, rejected_by_role, comment):
    recipients = set()

    if not expense.department:
        return

    # Initiator
    if expense.initiator and expense.initiator.email:
        initiator_email = expense.initiator.email
    else:
        initiator_email = None

    # Department Head (based on role)
    dept_head = User.objects.filter(
        department=expense.department,
        role="dept_head"
    ).first()
    dept_head_email = dept_head.email if dept_head and dept_head.email else None

    # Finance Team
    finance_users = User.objects.filter(
        department=expense.department,
        role="finance"
    )
    finance_emails = [u.email for u in finance_users if u.email]

    # Recipient logic
    if rejected_by_role == "DEPARTMENT_HEAD":
        if initiator_email:
            recipients.add(initiator_email)

    elif rejected_by_role == "FINANCE":
        if initiator_email:
            recipients.add(initiator_email)
        if dept_head_email:
            recipients.add(dept_head_email)

    elif rejected_by_role == "COO":
        if initiator_email:
            recipients.add(initiator_email)
        if dept_head_email:
            recipients.add(dept_head_email)
        recipients.update(finance_emails)

    if not recipients:
        return

    subject = f"Expense #{expense.id} Rejected"

    message = f"""
Expense ID: {expense.id}
Department: {expense.department.name}
Amount: {expense.amount}

Rejected By: {rejected_by_role}

Reason:
{comment}
"""

    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=list(recipients),
        fail_silently=False,
    )
