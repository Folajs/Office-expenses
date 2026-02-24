import pytest
from rest_framework.test import APIClient


@pytest.mark.django_db
def test_initiator_cannot_approve(expense, initiator):
    client = APIClient()
    client.force_authenticate(initiator)

    response = client.post(
        f"/api/approvals/department/{expense.id}/",
        {"action": "APPROVED"},
    )

    assert response.status_code == 403
