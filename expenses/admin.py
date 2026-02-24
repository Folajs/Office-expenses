from django.contrib import admin
from .models import Expense, ExpenseCategory, ExpenseDocument

admin.site.register(Expense)
admin.site.register(ExpenseCategory)
admin.site.register(ExpenseDocument)
