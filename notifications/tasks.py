from notifications.utils import send_expense_email
from users.models import User


def notify_expense_rejection(expense, rejected_by):
    recipients = set()

    # Always notify initiator
    if expense.initiator and expense.initiator.email:
        recipients.add(expense.initiator.email)

    if rejected_by.role == 'dept_head':
        # Only initiator
        pass

    elif rejected_by.role == 'finance':
        # Dept head + initiator
        dept_heads = User.objects.filter(
            department=expense.department,
            role='dept_head'
        )
        recipients.update([u.email for u in dept_heads if u.email])

    elif rejected_by.role == 'coo':
        # Finance + dept head + initiator
        dept_heads = User.objects.filter(
            department=expense.department,
            role='dept_head'
        )
        finance_users = User.objects.filter(role='finance')

        recipients.update([u.email for u in dept_heads if u.email])
        recipients.update([u.email for u in finance_users if u.email])

    if not recipients:
        return

    context = {
        'expense': expense,
        'rejected_by': rejected_by,
    }

    send_expense_email(
        subject=f"Expense Rejected: {expense.title}",
        template_name='notifications/email_rejection.html',
        context=context,
        recipient_list=list(recipients)
    )

def notify_expense_approval(expense, approved_by):
    recipients = set()

    # Dept Head approval → notify Finance
    if approved_by.role == "dept_head":
        finance_users = User.objects.filter(role="finance")
        recipients.update([u.email for u in finance_users if u.email])

    # Finance approval → notify COO
    elif approved_by.role == "finance":
        coo_users = User.objects.filter(role="coo")
        recipients.update([u.email for u in coo_users if u.email])

    # COO approval → FINAL → notify initiator
    elif approved_by.role == "coo":
        if expense.initiator and expense.initiator.email:
            recipients.add(expense.initiator.email)

    if not recipients:
        return

    is_final = expense.status == "APPROVED"

    context = {
        "expense": expense,
        "approved_by": approved_by,
        "is_final": is_final,
    }

    send_expense_email(
        subject=f"Expense Approved: {expense.title}",
        template_name="notifications/email_approval.html",
        context=context,
        recipient_list=list(recipients),
    )