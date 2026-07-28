from django.shortcuts import redirect
from django.contrib import messages

class RoleBasedAccessMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path.rstrip('/')
        
        # Identify protected admin paths
        is_admin_path = (
            path == '/admin' or 
            path.startswith('/admin/') or 
            path == '/admin-dashboard' or 
            path.startswith('/admin-dashboard/') or 
            path == '/admin-login' or 
            path == '/admin/settings'
        )

        if is_admin_path:
            # Check if user is logged in and possesses the admin role
            if not request.user.is_authenticated or request.user.role != 'admin':
                messages.error(request, "Access Denied. You do not have permission to access this page.")
                return redirect('home')

        response = self.get_response(request)
        return response
