from django.db import models
from django.contrib.auth.models import AbstractUser

class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)
    def __str__(self):
        return self.name

class User(AbstractUser):
    ROLE_CHOICES = [
        ('initiator', 'Expense Initiator'),
        ('dept_head', 'Department Head'),
        ('finance', 'Finance Team'),
        ('coo', 'Chief Operating Officer'),
        ('admin', 'System Administrator'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True)
    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
