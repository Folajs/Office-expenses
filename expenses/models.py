from django.db import models
from users.models import User
from users.models import Department
from django.conf import settings


class ExpenseCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Expense(models.Model):
    STATUS_PENDING = "PENDING"
    STATUS_FINANCE_REVIEW = "FINANCE_REVIEW"
    STATUS_COO_REVIEW = "COO_REVIEW"
    STATUS_APPROVED = "APPROVED"
    STATUS_REJECTED = "REJECTED"
    STATUS_PAID = "PAID"


    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_FINANCE_REVIEW, "Finance Review"),
        (STATUS_COO_REVIEW, "COO Review"),
        (STATUS_APPROVED, "Approved"),
        (STATUS_PAID, "Paid"),
        (STATUS_REJECTED, "Rejected"),
]

    initiator = models.ForeignKey(
        User, on_delete=models.PROTECT, related_name='initiated_expenses',
        db_index=True 
    )
    department = models.ForeignKey(
        Department, on_delete=models.PROTECT, related_name='expenses',
        db_index=True 
    )
    category = models.ForeignKey(
        ExpenseCategory, on_delete=models.PROTECT,
        db_index=True 
    )

    title = models.CharField(max_length=255)
    description = models.TextField()
    amount = models.DecimalField(max_digits=12, decimal_places=2)

    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING,
        db_index=True 
    )
    
    rejection_reason = models.TextField(null=True, blank=True)

    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="processed_expenses"
)

    processed_at = models.DateTimeField(null=True, blank=True)

    is_archived = models.BooleanField(default=False, db_index=True )

    created_at = models.DateTimeField(auto_now_add=True, db_index=True )
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        indexes = [
            models.Index(fields=["status", "created_at"]),
            models.Index(fields=["department", "status"]),
            models.Index(fields=["initiator", "status"]),
        ]


    def __str__(self):
        return f"{self.title} ({self.amount})"
    
    def can_transition(self, new_status):
        allowed_transitions = {
            "PENDING": ["FINANCE_REVIEW", "REJECTED"],
            "FINANCE_REVIEW": ["COO_REVIEW", "REJECTED"],
            "COO_REVIEW": ["APPROVED", "REJECTED"],
            "APPROVED": ["PAID"],
            "PAID": [],
             "REJECTED": [],
    }

        return new_status in allowed_transitions.get(self.status, [])

    paid_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="paid_expenses"
    )

    paid_at = models.DateTimeField(null=True, blank=True)

    payment_reference = models.CharField(
        max_length=100,
        null=True,
        blank=True
    )


class ExpenseDocument(models.Model):
    DOCUMENT_REQUEST = 'REQUEST'
    DOCUMENT_INVOICE = 'INVOICE'
    DOCUMENT_RECEIPT = 'RECEIPT'

    DOCUMENT_TYPES = [
        (DOCUMENT_REQUEST, 'Expense Request'),
        (DOCUMENT_INVOICE, 'Invoice'),
        (DOCUMENT_RECEIPT, 'Receipt'),
    ]

    expense = models.ForeignKey(
        Expense, on_delete=models.CASCADE, related_name='documents'
    )
    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPES)
    file = models.FileField(upload_to='expenses/documents/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

class ExpenseApprovalHistory(models.Model):

    ACTION_APPROVED = "APPROVED"
    ACTION_REJECTED = "REJECTED"

    ACTION_CHOICES = [
        (ACTION_APPROVED, "Approved"),
        (ACTION_REJECTED, "Rejected"),
    ]

    expense = models.ForeignKey(
        Expense,
        on_delete=models.CASCADE,
        related_name="approval_history",
        db_index=True
    )

    action = models.CharField(max_length=20, choices=ACTION_CHOICES)

    performed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True
    )

    comment = models.TextField(null=True, blank=True)

    timestamp = models.DateTimeField(auto_now_add=True,db_index=True)

    def __str__(self):
        return f"{self.expense.id} - {self.action} by {self.performed_by}"
    
    class Meta:
        indexes = [
            models.Index(fields=["expense", "timestamp"]),
        ]
