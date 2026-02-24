from django.urls import path
from .views import (
    DepartmentHeadApprovalView,
    FinanceApprovalView,
    COOApprovalView,
    ExpenseApprovalHistoryView
)

urlpatterns = [
    path("department/<int:expense_id>/", DepartmentHeadApprovalView.as_view()),
    path("finance/<int:expense_id>/", FinanceApprovalView.as_view()),
    path("coo/<int:expense_id>/", COOApprovalView.as_view()),
    path("history/<int:expense_id>/", ExpenseApprovalHistoryView.as_view(), name="expense-approval-history"),
]
