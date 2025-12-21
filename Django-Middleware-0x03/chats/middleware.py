import datetime
import time
from django.core.cache import cache
from django.http import HttpResponseForbidden
import logging

logger = logging.getLogger(__name__)


class RequestLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = request.user if request.user.is_authenticated else "Anonymous"
        log_message = (
            f"{datetime.datetime.now()} - User: {user} - Path: {request.path}\n"
        )
        logger.info(f"User: {user} - Path: {request.path}")
        return self.get_response(request)


class RestrictAccessByTimeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Exclude admin and auth to prevent lockout
        if request.path.startswith("/admin") or request.path.startswith("/api/"):
            return self.get_response(request)

        current_hour = datetime.datetime.now().hour
        # Business hours defined as 9:00 AM to 5:59 PM (18:00)
        if not (9 <= current_hour < 18):
            return HttpResponseForbidden("Access restricted outside business hours.")

        return self.get_response(request)


class OffensiveLanguageMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.method == 'POST':
            # Handle proxy IPs (e.g., Nginx/Heroku)
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            ip = x_forwarded_for.split(',')[0] if x_forwarded_for else request.META.get('REMOTE_ADDR')
            
            cache_key = f"ratelimit_{ip}"
            request_count = cache.get(cache_key, 0)

            if request_count >= 5:
                return HttpResponseForbidden("Rate limit exceeded. Try again in a minute.")
            
            # Increment and set expiry to 60 seconds
            cache.set(cache_key, request_count + 1, 60)

        return self.get_response(request)

class RolePermissionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Exclude public or administrative paths
        if request.path.startswith(("/admin", "/login", "/api/public")):
            return self.get_response(request)

        # 1. Check if user is even logged in
        if not request.user.is_authenticated:
            return HttpResponseForbidden("Authentication required.")

        # 2. Check for specific roles
        role = getattr(request.user, "role", "guest")
        if role not in ["admin", "moderator"]:
            return HttpResponseForbidden(
                "Access Denied: Admin or Moderator role required."
            )

        return self.get_response(request)
