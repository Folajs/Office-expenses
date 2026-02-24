import pytest
from django.contrib.auth import get_user_model
from users.models import Department
from expenses.models import Expense, ExpenseCategory

User = get_user_model()


@pytest.fixture
def department():
    return Department.objects.create(name="IT")


@pytest.fixture
def category():
    return ExpenseCategory.objects.create(name="Office Supplies")


@pytest.fixture
def initiator(department):
    return User.objects.create_user(
        username="initiator",
        email="initiator@test.com",
        password="pass1234",
        role="INITIATOR",
        department=department,
    )


@pytest.fixture
def dept_head(department):
    return User.objects.create_user(
        username="head",
        email="head@test.com",
        password="pass1234",
        role="DEPARTMENT_HEAD",
        department=department,
    )


@pytest.fixture
def finance(department):
    return User.objects.create_user(
        username="finance",
        email="finance@test.com",
        password="pass1234",
        role="FINANCE",
        department=department,
    )


@pytest.fixture
def coo():
    return User.objects.create_user(
        username="coo",
        email="coo@test.com",
        password="pass1234",
        role="COO",
    )


@pytest.fixture
def expense(initiator, department, category):
    return Expense.objects.create(
        initiator=initiator,
        department=department,
        category=category,
        amount=1000,
        status="PENDING",
    )
