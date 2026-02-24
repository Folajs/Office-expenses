from django.urls import path
from .views import (
    ExpenseCreateView,
    ExpenseUpdateView,
    ExpenseArchiveView,
    ExpenseHistoryView,
    DashboardStatsView,
    MarkExpenseAsPaidView,
    # ExpenseApproveView, 
    # ExpenseRejectView,
)

urlpatterns = [
    # Create expense → POST /api/expenses/
    path("", ExpenseCreateView.as_view(), name="expense-create"),

    # Update expense → PUT /api/expenses/<id>/
    path("<int:pk>/", ExpenseUpdateView.as_view(), name="expense-update"),

    # Archive expense → PATCH /api/expenses/<id>/archive/
    path("<int:pk>/archive/", ExpenseArchiveView.as_view(), name="expense-archive"),

    # History → GET /api/expenses/history/
    path("history/", ExpenseHistoryView.as_view(), name="expense-history"),

    path("dashboard/", DashboardStatsView.as_view(), name="expense-dashboard"),
    
    path("<int:pk>/mark-paid/", MarkExpenseAsPaidView.as_view()),

    # path("<int:pk>/approve/", ExpenseApproveView.as_view(), name="expense-approve"),
    # path("<int:pk>/reject/", ExpenseRejectView.as_view(), name="expense-reject"),

]

# from django.urls import path
# from .views import (
#     ExpenseCreateView,
#     ExpenseUpdateView,
#     ExpenseArchiveView,
#     ExpenseHistoryView
# )

# urlpatterns = [
#     path('create/', ExpenseCreateView.as_view()),
#     path('<int:pk>/update/', ExpenseUpdateView.as_view()),
#     path('<int:pk>/archive/', ExpenseArchiveView.as_view()),
#     path('history/', ExpenseHistoryView.as_view()),
# ]
