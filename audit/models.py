from django.db import models
from users.models import User

class AuditLog(models.Model):
    ACTION_CHOICES = [
        ('submit', 'Submit Expense'),
        ('approve', 'Approve Expense'),
        ('reject', 'Reject Expense'),
        ('payment', 'Payment Processed'),
        ('login', 'User Login'),
        ('logout', 'User Logout'),
    ]

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    role = models.CharField(max_length=20)
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    target_model = models.CharField(max_length=50)
    target_id = models.IntegerField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    comments = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.timestamp} | {self.user} | {self.action} | {self.target_model}({self.target_id})"
