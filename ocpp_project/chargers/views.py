from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from .services import ChargingRequestService
from .serializers import CommandSerializer, TransactionSerializer, ChargerSerializer
from .models import Transaction,Charger
from.choices import ChargerStatus

class SendCommandAPIView(APIView):
    # permission_classes = [IsAuthenticated]

    def post(self, request, charger_name):

        serializer = CommandSerializer(data=request.data)
        if serializer.is_valid():
            command = serializer.validated_data.get("command")
            ChargingRequestService.send_command_request(charger_name, command)
            return Response({"status": "success", "command": command}, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class TransactionListView(APIView):
    # permission_classes = [IsAuthenticated]
    def get(self, request):
        transactions = Transaction.objects.all().order_by('-start_time')
        serializer = TransactionSerializer(transactions, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

class ConnectedChargersView(APIView):
    # permission_classes = [IsAuthenticated]
    def get(self, request):
        connected_chargers = Charger.objects.filter(status=ChargerStatus.CONNECTED)
        serializer = ChargerSerializer(connected_chargers, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)