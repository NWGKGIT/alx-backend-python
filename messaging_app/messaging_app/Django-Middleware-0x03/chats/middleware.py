import datetime
import time
from django.http import HttpResponseForbidden, JsonResponse
from django.conf import settings

# In-memory storage for IP tracking (Task 3)
# Structure: { '127.0.0.1': [timestamp1, timestamp2, ...] }
IP_MESSAGE_LOG = {}

class RequestLoggingMiddleware:
    """
    Task 1: Logs each user's requests to a file (requests.log).
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = request.user if request.user.is_authenticated else "Anonymous"
        log_message = f"{datetime.datetime.now()} - User: {user} - Path: {request.path}\n"
        
        # Open file in Append mode
        try:
            with open('requests.log', 'a') as f:
                f.write(log_message)
        except Exception as e:
            # Handle potential file permission errors silently or print to console
            print(f"Error logging request: {e}")

        response = self.get_response(request)
        return response


class RestrictAccessByTimeMiddleware:
    """
    Task 2: Restrict access to the messaging app during certain hours.
    Intepretation: 'Outside 9PM and 6PM'. 
    Logic implemented: Allow access only between 9 AM and 6 PM (Business Hours).
    If the prompt strictly means 'Night only' (9PM to 6PM), change the logic accordingly.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        current_hour = datetime.datetime.now().hour
        
        # Assuming allowed hours are 9 AM (9) to 6 PM (18)
        # If current hour is LESS than 9 OR GREATER/EQUAL to 18 (6PM), deny access.
        # NOTE: Exclude admin/auth endpoints so users can still potentially login/manage site
        if not request.path.startswith('/admin') and not request.path.startswith('/api/token'):
            if current_hour < 9 or current_hour >= 18:
                return HttpResponseForbidden("Access restricted outside business hours (9AM - 6PM).")

        response = self.get_response(request)
        return response


class OffensiveLanguageMiddleware:
    """
    Task 3: Limit the number of chat messages (POST requests) per IP address.
    (5 messages per 1 minute window).
    """
    def __init__(self, get_response):
        self.get_response = get_response
        self.limit = 5
        self.window = 60  # seconds

    def __call__(self, request):
        # Only track POST requests (sending messages)
        if request.method == 'POST':
            # Get IP Address
            ip = self.get_client_ip(request)
            current_time = time.time()

            # Initialize IP in log if not present
            if ip not in IP_MESSAGE_LOG:
                IP_MESSAGE_LOG[ip] = []

            # Filter out timestamps older than the window (1 minute)
            IP_MESSAGE_LOG[ip] = [t for t in IP_MESSAGE_LOG[ip] if current_time - t < self.window]

            # Check limit
            if len(IP_MESSAGE_LOG[ip]) >= self.limit:
                return HttpResponseForbidden("Message limit exceeded. Please wait a moment.")

            # Log this new message timestamp
            IP_MESSAGE_LOG[ip].append(current_time)

        response = self.get_response(request)
        return response

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class RolepermissionMiddleware:
    """
    Task 4: Check user role (admin/moderator) before allowing access.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Define roles allowed
        allowed_roles = ['admin', 'moderator']
        
        # Exclude admin site, auth endpoints, and safe methods (GET) if intended to only block actions
        # However, prompt implies blocking "access".
        # We MUST exclude admin/ and login paths to prevent lockout.
        excluded_paths = ['/admin/', '/api/token/', '/api-auth/']
        
        if any(request.path.startswith(path) for path in excluded_paths):
            return self.get_response(request)

        if request.user.is_authenticated:
            # Assuming the CustomUser model has a 'role' field as per previous project
            user_role = getattr(request.user, 'role', 'guest')
            
            # If user is superuser, always allow
            if request.user.is_superuser:
                return self.get_response(request)

            if user_role not in allowed_roles:
                return HttpResponseForbidden(f"Access Denied: User role '{user_role}' is not authorized.")
        
        # If user is not authenticated, standard permissions will handle it, 
        # or we block them here depending on strictness.
        
        response = self.get_response(request)
        return response