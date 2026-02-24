import pytest
from rest_framework.test import APIClient


@pytest.mark.django_db
def test_non_finance_cannot_export_csv(initiator):
    client = APIClient()
    client.force_authenticate(initiator)

    response = client.get("/api/reports/export/csv/")
    assert response.status_code == 403
