import csv
from django.http import HttpResponse
from expenses.models import Expense


def export_expenses_csv(queryset=None):
    """
    Export expenses as CSV.
    Used by Finance / Admin users.
    """

    if queryset is None:
        queryset = Expense.objects.select_related(
            "department",
            "category",
            "initiator",
            "approved_by",
        )

    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="expenses_report.csv"'

    writer = csv.writer(response)

    writer.writerow([
        "Expense ID",
        "Department",
        "Category",
        "Amount",
        "Status",
        "Initiator Email",
        "Approved By",
        "Processed At",
        "Created At",
    ])

    for expense in queryset:
        writer.writerow([
            expense.id,
            expense.department.name if expense.department else "",
            expense.category.name if expense.category else "",
            expense.amount,
            expense.status,
            expense.initiator.email if expense.initiator else "",
            expense.approved_by.email if expense.approved_by else "",
            expense.processed_at.strftime("%Y-%m-%d %H:%M") if expense.processed_at else "",
            expense.created_at.strftime("%Y-%m-%d %H:%M"),
        ])

    return response
