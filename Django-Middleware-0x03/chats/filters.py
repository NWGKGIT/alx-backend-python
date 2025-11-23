# chats/filters.py

import django_filters
from .models import Message

class MessageFilter(django_filters.FilterSet):
    # Filter by date range (e.g., ?start_date=2024-01-01&end_date=2024-01-31)
    start_date = django_filters.DateFilter(field_name="sent_at", lookup_expr='gte')
    end_date = django_filters.DateFilter(field_name="sent_at", lookup_expr='lte')
    
    # Filter by sender email (e.g., ?sender=john@example.com)
    sender = django_filters.CharFilter(field_name="sender__email", lookup_expr='icontains')

    class Meta:
        model = Message
        fields = ['start_date', 'end_date', 'sender']