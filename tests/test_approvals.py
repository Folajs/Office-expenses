import pytest
from rest_framework.test import APIClient


@pytest.mark.django_db
def test_department_head_can_approve(expense, dept_head):
    client = APIClient()
    client.force_authenticate(dept_head)

    response = client.post(
        f"/api/approvals/department/{expense.id}/",
        {"action": "APPROVED"},
    )

    assert response.status_code == 200
    expense.refresh_from_db()
    assert expense.status == "FINANCE_REVIEW"


@pytest.mark.django_db
def test_cannot_skip_approval_level(expense, finance):
    client = APIClient()
    client.force_authenticate(finance)

    response = client.post(
        f"/api/approvals/finance/{expense.id}/",
        {"action": "APPROVED"},
    )

    assert response.status_code == 400
    assert "must be in" in response.data["detail"]


@pytest.mark.django_db
def test_rejection_finalizes_expense(expense, dept_head):
    client = APIClient()
    client.force_authenticate(dept_head)

    response = client.post(
        f"/api/approvals/department/{expense.id}/",
        {"action": "REJECTED", "comment": "Invalid receipt"},
    )

    assert response.status_code == 200
    expense.refresh_from_db()
    assert expense.status == "REJECTED"
