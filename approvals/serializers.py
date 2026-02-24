from rest_framework import serializers
from .models import ApprovalLog


class ApprovalActionSerializer(serializers.Serializer):
    action = serializers.ChoiceField(choices=["APPROVED", "REJECTED"])
    comment = serializers.CharField(required=False, allow_blank=True)


class ApprovalLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApprovalLog
        fields = "__all__"

class ApprovalLogSerializer(serializers.ModelSerializer):
    action_by = serializers.StringRelatedField()
    
    class Meta:
        model = ApprovalLog
        fields = [
            "id",
            "expense",
            "action_by",
            "role",
            "action",
            "comment",
            "created_at",
        ]
