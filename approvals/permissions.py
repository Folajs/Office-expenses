from rest_framework.permissions import BasePermission


class IsDepartmentHead(BasePermission):
    def has_permission(self, request, view):
        return request.user.role == "dept_head"


class IsFinanceTeam(BasePermission):
    def has_permission(self, request, view):
        return request.user.role == "finance"


class IsCOO(BasePermission):
    def has_permission(self, request, view):
        return request.user.role == "coo"
