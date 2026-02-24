from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum, Count

from expenses.models import Expense
from permissions.permissions import IsFinanceOrAdmin
from .exports import export_expenses_csv


class ExpenseByDepartmentReportView(APIView):
    permission_classes = [IsAuthenticated, IsFinanceOrAdmin]

    def get(self, request):
        queryset = Expense.objects.all()

        # Optional status filter
        status = request.query_params.get("status")
        if status:
            queryset = queryset.filter(status=status)

        # Optional date filters
        start_date = request.query_params.get("start_date")
        end_date = request.query_params.get("end_date")

        if start_date and end_date:
            queryset = queryset.filter(created_at__range=[start_date, end_date])

        queryset = (
            queryset.values("department__name")
            .annotate(
                total_amount=Sum("amount"),
                expense_count=Count("id"),
            )
        )

        data = [
            {
                "label": item["department__name"],
                "total_amount": item["total_amount"] or 0,
                "expense_count": item["expense_count"],
            }
            for item in queryset
        ]

        return Response(data)


class ExpenseByCategoryReportView(APIView):
    permission_classes = [IsAuthenticated, IsFinanceOrAdmin]

    def get(self, request):
        queryset = Expense.objects.all()

        status = request.query_params.get("status")
        if status:
            queryset = queryset.filter(status=status)

        start_date = request.query_params.get("start_date")
        end_date = request.query_params.get("end_date")

        if start_date and end_date:
            queryset = queryset.filter(created_at__range=[start_date, end_date])

        queryset = (
            queryset.values("category__name")
            .annotate(
                total_amount=Sum("amount"),
                expense_count=Count("id"),
            )
        )

        data = [
            {
                "label": item["category__name"],
                "total_amount": item["total_amount"] or 0,
                "expense_count": item["expense_count"],
            }
            for item in queryset
        ]

        return Response(data)


class ExpenseByEmployeeReportView(APIView):
    permission_classes = [IsAuthenticated, IsFinanceOrAdmin]

    def get(self, request):
        queryset = Expense.objects.all()

        status = request.query_params.get("status")
        if status:
            queryset = queryset.filter(status=status)

        start_date = request.query_params.get("start_date")
        end_date = request.query_params.get("end_date")

        if start_date and end_date:
            queryset = queryset.filter(created_at__range=[start_date, end_date])

        queryset = (
            queryset.values("initiator__email")
            .annotate(
                total_amount=Sum("amount"),
                expense_count=Count("id"),
            )
        )

        data = [
            {
                "label": item["initiator__email"],
                "total_amount": item["total_amount"] or 0,
                "expense_count": item["expense_count"],
            }
            for item in queryset
        ]

        return Response(data)


class FinancialSummaryView(APIView):
    permission_classes = [IsAuthenticated, IsFinanceOrAdmin]

    def get(self, request):
        queryset = Expense.objects.all()

        total_requested = queryset.aggregate(
            total=Sum("amount")
        )["total"] or 0

        total_approved = queryset.filter(
            status="APPROVED"
        ).aggregate(total=Sum("amount"))["total"] or 0

        total_paid = queryset.filter(
            status="PAID"
        ).aggregate(total=Sum("amount"))["total"] or 0

        total_rejected = queryset.filter(
            status="REJECTED"
        ).aggregate(total=Sum("amount"))["total"] or 0

        return Response({
            "total_requested": total_requested,
            "total_approved": total_approved,
            "total_paid": total_paid,
            "total_rejected": total_rejected,
        })


class ExpenseCSVExportView(APIView):
    permission_classes = [IsAuthenticated, IsFinanceOrAdmin]

    def get(self, request):
        queryset = Expense.objects.select_related(
            "department",
            "category",
            "initiator",
            "approved_by",
        )

        status = request.query_params.get("status")
        if status:
            queryset = queryset.filter(status=status)

        start_date = request.query_params.get("start_date")
        end_date = request.query_params.get("end_date")

        if start_date and end_date:
            queryset = queryset.filter(created_at__range=[start_date, end_date])

        return export_expenses_csv(queryset)
