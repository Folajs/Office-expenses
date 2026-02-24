from django.db.models import Sum
from django.utils import timezone
from rest_framework import generics
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from .models import ExpenseApprovalHistory
from .permissions import CanProcessExpense
from .models import Expense
from .serializers import ExpenseSerializer
from .permissions import IsExpenseInitiator, CanModifyExpense
from .services import attach_document
# from notifications.services import send_templated_email


class ExpenseCreateView(generics.CreateAPIView):
    serializer_class = ExpenseSerializer
    permission_classes = [IsAuthenticated, IsExpenseInitiator]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def perform_create(self, serializer):    
       user = self.request.user
       expense = serializer.save(       
           initiator=user,
           department=user.department
    )

       files = self.request.FILES.getlist('documents')
       for file in files:
            attach_document(expense, 'REQUEST', file)
       
       # 📧 Send notification email to department head
    #    if expense.department.head and expense.department.head.email:
    #     send_templated_email(
    #         subject="New Expense Submitted",
    #         template_name="emails/expense_submitted.html",
    #         context={"expense": expense},
    #         recipient_list=[expense.department.head.email],
    #     )


class ExpenseUpdateView(generics.UpdateAPIView):
    serializer_class = ExpenseSerializer
    permission_classes = [CanModifyExpense]
    queryset = Expense.objects.select_related(
        "initiator",
        "department"
    )
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def perform_update(self, serializer):
        expense = self.get_object()
        if expense.status != Expense.STATUS_PENDING:
            raise PermissionDenied("Cannot modify processed expense.")
        serializer.save()
        if expense.is_archived:
            raise PermissionDenied("Cannot modify archived expense.")



class ExpenseArchiveView(generics.UpdateAPIView):
    queryset = Expense.objects.only("id", "is_archived")
    permission_classes = [CanModifyExpense]

    def update(self, request, *args, **kwargs):
        expense = self.get_object()
        expense.is_archived = True
        expense.save(update_fields=['is_archived'])
        return Response({"detail": "Expense archived."})


class ExpenseHistoryView(generics.ListAPIView):
    serializer_class = ExpenseSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):      
          user = self.request.user

          qs = Expense.objects.select_related(
             "initiator",
             "department",
             "category",
             "approved_by",
             "paid_by",
         ).filter(is_archived=False)

          status = self.request.query_params.get('status')
          category = self.request.query_params.get('category')

          if status:        
             qs = qs.filter(status=status)

          if category:
             qs = qs.filter(category_id=category)

    # 🔐 Role-based visibility enforcement
          if user.role == "initiator":
             qs = qs.filter(initiator=user)

          elif user.role == "dept_head":
             qs = qs.filter(
                 
                department=user.department,
                status="PENDING"
             )

          elif user.role == "finance":
             qs = qs.filter(                        
                 status__in=["FINANCE_REVIEW", "APPROVED"]
              )

          elif user.role == "coo":
             qs = qs.filter(status="COO_REVIEW")

          elif user.role == "admin":
             pass

          return qs.order_by("-created_at")


class DashboardStatsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        qs = Expense.objects.filter(
            is_archived=False
        ).only(
            "id",
            "amount",
            "status",
            "initiator",
            "department"
    )


        # 🔐 Role-based filtering
        if user.role == "initiator":
            qs = qs.filter(initiator=user)

        elif user.role == "dept_head":
            qs = qs.filter(
                department=user.department,
                status="PENDING"
            )

        elif user.role == "finance":
            qs = qs.filter(status="FINANCE_REVIEW")

        elif user.role == "coo":
            qs = qs.filter(status="COO_REVIEW")

        elif user.role == "admin":
            pass

        total_pending = qs.count()
        total_amount = qs.aggregate(total=Sum("amount"))["total"] or 0

        return Response({
            "total_pending": total_pending,
            "total_amount": total_amount
        })

class MarkExpenseAsPaidView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        try:
            expense = Expense.objects.select_related(
                "initiator",
                "department"
            ).filter(
                pk=pk,
                is_archived=False
            ).first()

            if not expense:
                return Response({"detail": "Expense not found."}, status=404)
        except Expense.DoesNotExist:
            return Response({"detail": "Expense not found."}, status=404)

        user = request.user

        # 🔐 Only finance or admin can mark as paid
        if user.role not in ["finance", "admin"]:
            raise PermissionDenied("Only finance can mark expense as paid.")

        if expense.status != Expense.STATUS_APPROVED:
            return Response(
                {"detail": "Only approved expenses can be marked as paid."},
                status=400
            )

        if not expense.can_transition(Expense.STATUS_PAID):
            return Response(
                {"detail": "Invalid status transition."},
                status=400
            )

        expense.status = Expense.STATUS_PAID
        expense.paid_by = user
        expense.paid_at = timezone.now()
        expense.payment_reference = request.data.get("payment_reference")

        expense.save()

        return Response({
            "detail": "Expense marked as paid.",
            "paid_at": expense.paid_at,
            "payment_reference": expense.payment_reference
        })

