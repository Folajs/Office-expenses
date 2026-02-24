from rest_framework.response import Response
from rest_framework import status

def department_isolation(view_func):
    def _wrapped_view(self, request, *args, **kwargs):
        obj = getattr(self, 'get_object', lambda: None)()
        if obj and hasattr(request.user, 'department') and obj.department != request.user.department:
            return Response({'detail': 'Access denied for other departments.'}, status=status.HTTP_403_FORBIDDEN)
        return view_func(self, request, *args, **kwargs)
    return _wrapped_view
