from django.urls import path
from .views import (
    ExpenseByDepartmentReportView,
    ExpenseByCategoryReportView,
    ExpenseByEmployeeReportView,
    ExpenseCSVExportView,
    FinancialSummaryView,
)

urlpatterns = [
    path(
        "by-department/",
        ExpenseByDepartmentReportView.as_view(),
        name="report-by-department",
    ),
    path(
        "by-category/",
        ExpenseByCategoryReportView.as_view(),
        name="report-by-category",
    ),
    path(
        "by-employee/",
        ExpenseByEmployeeReportView.as_view(),
        name="report-by-employee",
    ),
    path(
        "financial-summary/",
        FinancialSummaryView.as_view(),
        name="financial-summary",
    ),
    path(
        "export/csv/",
        ExpenseCSVExportView.as_view(),
        name="report-export-csv",
    ),
]
