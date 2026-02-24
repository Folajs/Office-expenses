from django.utils import timezone
from approvals.models import Approval
from expenses.models import Expense
from audit.utils import log_action
from approvals.utils import send_rejection_email


def process_approval(*, expense: Expense, user, action: str, comment: str = ""):
    """
    action: APPROVE | REJECT
    """

    approval = Approval.objects.create(
        expense=expense,
        approved_by=user,
        role=user.role,
        action=action,
        comment=comment,
        acted_at=timezone.now(),
    )

    if action == "REJECT":
        expense.status = Expense.Status.REJECTED
        expense.save(update_fields=["status"])

        send_rejection_email(
            expense=expense,
            rejected_by_role=user.role,
        )

    elif action == "APPROVE":
        expense.advance_status()

    log_action(
        user=user,
        action=f"{action} expense",
        target=expense,
        metadata={"role": user.role},
    )

    return approval
