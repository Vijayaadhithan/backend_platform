from rest_framework import permissions
from django.conf import settings

def get_permission_classes(staff_only=False):
    """
    Dynamically returns permission classes based on security settings.
    
    Args:
        staff_only (bool): If True, returns IsAdminUser when security is enabled
                          If False, returns IsAuthenticated when security is enabled
    
    Returns:
        list: List of permission classes to use
    """
    # If DEBUG_SECURITY is True, return AllowAny to disable security checks
    if settings.DEBUG_SECURITY:
        return [permissions.AllowAny]
    
    # If security is enabled, return appropriate permission class
    if staff_only:
        return [permissions.IsAdminUser]
    else:
        return [permissions.IsAuthenticated]