from rest_framework import serializers
from .models import Expense, ExpenseDocument, ExpenseApprovalHistory
from approvals.serializers import ApprovalLogSerializer

class ExpenseApprovalHistorySerializer(serializers.ModelSerializer):
    performed_by_email = serializers.EmailField(
        source="performed_by.email",
        read_only=True
    )

    class Meta:
        model = ExpenseApprovalHistory
        fields = [
            "id",
            "action",
            "comment",
            "performed_by",
            "performed_by_email",
            "timestamp",
        ]


class ExpenseDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExpenseDocument
        fields = [
            "id",
            "document_type",
            "file",
            "uploaded_at",
        ]

class ExpenseSerializer(serializers.ModelSerializer):
    documents = ExpenseDocumentSerializer(many=True, read_only=True)

    initiator_email = serializers.EmailField(
        source="initiator.email",
        read_only=True,
    )

    department_name = serializers.CharField(
        source="department.name",
        read_only=True,
    )

    category_name = serializers.CharField(
        source="category.name",
        read_only=True,
    )

    approved_by_email = serializers.EmailField(
        source="approved_by.email",
        read_only=True
    )

    approval_history = serializers.SerializerMethodField()
    next_approval_role = serializers.SerializerMethodField()

    class Meta:
        model = Expense
        fields = [
            "id",
            "title",
            "amount",
            "description",
            "status",
            "rejection_reason",
            "department",
            "department_name",
            "category",
            "category_name",
            "initiator",
            "initiator_email",
            "approved_by",
            "approved_by_email",
            "processed_at",
            "created_at",
            "documents",
            "approval_history",
            "next_approval_role",
        ]

        read_only_fields = [
            "status",
            "initiator",
            "department",
            "approved_by",
            "processed_at",
            "created_at",
        ]

    def get_approval_history(self, obj):
        logs = obj.approval_logs.all().order_by("created_at")
        return ApprovalLogSerializer(logs, many=True).data

    def get_next_approval_role(self, obj):
        mapping = {
            "PENDING": "DEPARTMENT_HEAD",
            "FINANCE_REVIEW": "FINANCE",
            "COO_REVIEW": "COO",
        }
        return mapping.get(obj.status)
