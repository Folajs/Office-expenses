from django.utils.dateparse import parse_date
from django.db import transaction
from django.utils import timezone
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from expenses.models import Expense
from .models import ApprovalLog
from .serializers import ApprovalActionSerializer, ApprovalLogSerializer
from notifications.tasks import notify_expense_rejection,notify_expense_approval



class BaseApprovalView(APIView):
    permission_classes = [IsAuthenticated]

    ROLE = None
    NEXT_STATUS = None
    EXPECTED_PREVIOUS_STATUS = None

    def post(self, request, expense_id):
        with transaction.atomic():        
         expense = Expense.objects.select_for_update().get(id=expense_id)
     
        
         # 🚫 Prevent self-approval
         if expense.initiator == request.user:       
            return Response(
                {"detail": "You cannot approve or reject your own expense."},
                status=403,
            )

        # 🔐 Department isolation (Department Head can only approve their department)
         if self.ROLE == "dept_head":
            if expense.department != request.user.department:
                return Response(
                    {"detail": "You can only approve expenses from your department."},
                    status=403,
                )

        # 🔐 Role enforcement
         if request.user.role != self.ROLE:
            return Response(
                {"detail": "You are not allowed to perform this approval."},
                status=403,
            )

        # 🔁 Prevent re-approving finalized expenses
         if expense.status in ["REJECTED", "APPROVED"]:
            return Response(
                {"detail": "This expense has already been finalized."},
                status=400,
            )

        # 🔄 Enforce approval sequence
         if expense.status != self.EXPECTED_PREVIOUS_STATUS:
            return Response(
                {
                    "detail": (
                        f"Expense must be in '{self.EXPECTED_PREVIOUS_STATUS}' "
                        f"status before this approval."
                    )
                },
                status=400,
            )

         serializer = ApprovalActionSerializer(data=request.data)
         serializer.is_valid(raise_exception=True)

         action = serializer.validated_data["action"]
         comment = serializer.validated_data.get("comment", "")

         if action == "REJECTED":    
           
           if not expense.can_transition("REJECTED"):       
              return Response(       
                 {"detail": "Invalid status transition."},
                 status=400,
              )

           expense.status = "REJECTED"
           expense.approved_by = request.user
           expense.processed_at = timezone.now()
           expense.save(update_fields=["status", "approved_by", "processed_at"])
           
           # Manadatory email rejection
           notify_expense_rejection(        
              expense=expense,
              rejected_by=request.user,
)


         else:
             # 🔐 Enforce valid status transition
            if not expense.can_transition(self.NEXT_STATUS):
                return Response(         
                   {"detail": "Invalid status transition."},
                   status=400,
                )
            expense.status = self.NEXT_STATUS
            expense.approved_by = request.user
            expense.processed_at = timezone.now()
            expense.save(update_fields=["status", "approved_by", "processed_at"])

            notify_expense_approval(
                expense=expense,
                approved_by=request.user,
            )


        # 🧾 Audit log (mandatory for compliance)
         ApprovalLog.objects.create(
            expense=expense,
            action_by=request.user,
            role=self.ROLE,
            action=action,
            comment=comment,
        )

         return Response({"status": expense.status})


class DepartmentHeadApprovalView(BaseApprovalView):
    ROLE = "dept_head"
    EXPECTED_PREVIOUS_STATUS = "PENDING"
    NEXT_STATUS = "FINANCE_REVIEW"


class FinanceApprovalView(BaseApprovalView):
    ROLE = "finance"
    EXPECTED_PREVIOUS_STATUS = "FINANCE_REVIEW"
    NEXT_STATUS = "COO_REVIEW"


class COOApprovalView(BaseApprovalView):
    ROLE = "coo"
    EXPECTED_PREVIOUS_STATUS = "COO_REVIEW"
    NEXT_STATUS = "APPROVED"


class ExpenseApprovalHistoryView(generics.ListAPIView):
    serializer_class = ApprovalLogSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        expense_id = self.kwargs.get("expense_id")
        user = self.request.user
        queryset = ApprovalLog.objects.filter(expense_id=expense_id)

        # 🔐 Role-based visibility
        if user.role == "initiator":
            queryset = queryset.filter(expense__initiator=user)
        elif user.role == "dept_head":
            queryset = queryset.filter(expense__department=user.department)

        # 🔎 Filtering
        action = self.request.query_params.get("action")
        role = self.request.query_params.get("role")
        start_date = self.request.query_params.get("start_date")
        end_date = self.request.query_params.get("end_date")

        if action:
            queryset = queryset.filter(action=action.upper())

        if role:
            queryset = queryset.filter(role=role)

        if start_date:
            queryset = queryset.filter(created_at__date__gte=parse_date(start_date))

        if end_date:
            queryset = queryset.filter(created_at__date__lte=parse_date(end_date))

        return queryset.order_by("-created_at")
