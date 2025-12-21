# messaging_app/chats/urls.py
from django.urls import path, include
from rest_framework_nested import routers
from .views import ConversationViewSet, MessageViewSet
from .auth import RegisterView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
# Main Router
router = routers.DefaultRouter()
router.register(r"conversations", ConversationViewSet, basename="conversation")

# Nested Router
# lookup='conversation' creates a URL arg named 'conversation_pk'
conversations_router = routers.NestedSimpleRouter(
    router, r"conversations", lookup="conversation"
)
conversations_router.register(
    r"messages", MessageViewSet, basename="conversation-messages"
)

# Standalone Message Router (if checker requires it separately)
message_router = routers.DefaultRouter()
message_router.register(r"messages", MessageViewSet, basename="message")

urlpatterns = [
    path("auth/register/", RegisterView.as_view(), name="register"),
    path("auth/login/", TokenObtainPairView.as_view(), name="login"),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path("", include(router.urls)),
    path("", include(conversations_router.urls)),
    path("", include(message_router.urls)),
]
