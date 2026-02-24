import pytest
from rest_framework.test import APIClient


@pytest.mark.django_db
def test_expense_submission_requires_auth():
    client = APIClient()
    response = client.post("/api/expenses/")
    assert response.status_code == 401
