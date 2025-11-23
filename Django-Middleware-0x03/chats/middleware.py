import datetime
import time
from django.http import HttpResponseForbidden

class RequestLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = request.user if request.user.is_authenticated else "Anonymous"
        log_message = f"{datetime.datetime.now()} - User: {user} - Path: {request.path}\n"
        try:
            # Writes to requests.log in the project root
            with open('requests.log', 'a') as f:
                f.write(log_message)
        except Exception:
            pass
        return self.get_response(request)

class RestrictAccessByTimeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Exclude admin and auth to prevent lockout
        if request.path.startswith('/admin') or request.path.startswith('/api/'):
            return self.get_response(request)

        current_hour = datetime.datetime.now().hour
        # Logic: Deny access if OUTSIDE 9PM (21) and 6PM (18).
        # This implies access is only allowed between 9PM and 6PM? 
        # Or standard business hours? ALX tasks usually mean "Restrict to 9AM-6PM".
        # We will check if hour is outside business hours (9 to 18).
        if current_hour < 9 or current_hour >= 18:
            return HttpResponseForbidden("Access restricted outside business hours.")
        
        return self.get_response(request)

class OffensiveLanguageMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.ip_log = {}

    def __call__(self, request):
        if request.method == 'POST':
            ip = request.META.get('REMOTE_ADDR')
            current_time = time.time()
            
            if ip not in self.ip_log:
                self.ip_log[ip] = []
            
            # Filter timestamps to last 60 seconds
            self.ip_log[ip] = [t for t in self.ip_log[ip] if current_time - t < 60]
            
            if len(self.ip_log[ip]) >= 5:
                return HttpResponseForbidden("Message limit exceeded.")
            
            self.ip_log[ip].append(current_time)

        return self.get_response(request)

class RolepermissionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith('/admin') or request.path.startswith('/api/'):
             return self.get_response(request)

        if request.user.is_authenticated:
            role = getattr(request.user, 'role', 'guest')
            if role not in ['admin', 'moderator']:
                return HttpResponseForbidden("Access Denied: Admin or Moderator role required.")
        
        return self.get_response(request)