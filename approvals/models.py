from django.db import models
from django.conf import settings
from expenses.models import Expense


class ApprovalLog(models.Model):
    ROLE_CHOICES = (
        ("DEPARTMENT_HEAD", "Department Head"),
        ("FINANCE", "Finance"),
        ("COO", "Chief Operating Officer"),
    )

    ACTION_CHOICES = (
        ("APPROVED", "Approved"),
        ("REJECTED", "Rejected"),
    )

    expense = models.ForeignKey(
        Expense, on_delete=models.CASCADE, related_name="approval_logs"
    )
    action_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    action = models.CharField(max_length=10, choices=ACTION_CHOICES)
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]
