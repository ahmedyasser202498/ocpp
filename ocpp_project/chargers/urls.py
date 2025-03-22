from django.urls import path
from .views import SendCommandAPIView, TransactionListView,ConnectedChargersView

urlpatterns = [
    path('chargers/<str:charger_name>/send_command/', SendCommandAPIView.as_view(), name='send_command'),
    path('transactions/', TransactionListView.as_view(), name='api_transaction_list'),
    path('chargers/connected/', ConnectedChargersView.as_view(), name='api_connected_chargers')
]
