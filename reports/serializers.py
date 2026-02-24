from rest_framework import serializers


class ExpenseReportSerializer(serializers.Serializer):
    label = serializers.CharField()
    total_amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    count = serializers.IntegerField()
