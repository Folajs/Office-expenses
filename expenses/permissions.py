from rest_framework.permissions import BasePermission

class IsExpenseInitiator(BasePermission):
    def has_permission(self, request, view):
        return request.user.role == 'initiator'


class CanModifyExpense(BasePermission):
    def has_object_permission(self, request, view, obj):
        return (
            obj.initiator == request.user
            and obj.status == 'PENDING'
        )

class CanProcessExpense(BasePermission):

    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        user = request.user

        if obj.is_archived:
            return False

        if obj.status != 'PENDING':
            return False

        if obj.initiator == user:
            return False

        if user.role == 'dept_head' and user.department == obj.department:
            return True

        if user.role in ['finance', 'coo', 'admin']:
            return True

        return False


# from rest_framework.permissions import BasePermission

# class IsExpenseInitiator(BasePermission):
#     def has_permission(self, request, view):
#         return request.user.role == 'INITIATOR'


# class CanModifyExpense(BasePermission):
#     def has_object_permission(self, request, view, obj):
#         return (
#             obj.initiator == request.user
#             and obj.status == 'PENDING'
#         )
