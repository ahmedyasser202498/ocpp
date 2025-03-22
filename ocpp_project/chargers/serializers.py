from rest_framework import serializers
from .models import Transaction,Charger


class CommandSerializer(serializers.Serializer):
    command = serializers.JSONField()

    def validate(self, data):
        action = data.get("command", {}).get("action")
        req_data = data.get("command", {}).get("req_data")

        if action == "BootNotification":
            BootNotificationSerializer(data=req_data).is_valid(raise_exception=True)
        elif action == "Authorize":
            AuthorizeSerializer(data=req_data).is_valid(raise_exception=True)
        elif action == "StartTransaction" or action == "StartRemoteTransaction":
            StartTransactionSerializer(data=req_data).is_valid(raise_exception=True)
        elif action == "StopTransaction" or action == "StopRemoteTransaction":
            StopTransactionSerializer(data=req_data).is_valid(raise_exception=True)
        elif action == "Heartbeat":
            pass
        else:
            raise serializers.ValidationError("Invalid action type")

        return data

class BootNotificationSerializer(serializers.Serializer):
    chargeBoxSerialNumber = serializers.CharField(max_length=100)
    chargePointModel = serializers.CharField(max_length=100)
    chargePointSerialNumber = serializers.CharField(max_length=100)
    chargePointVendor = serializers.CharField(max_length=100)
    firmwareVersion = serializers.CharField(max_length=50)
    iccid = serializers.CharField(max_length=20)
    imsi = serializers.CharField(max_length=20)
    meterSerialNumber = serializers.CharField(max_length=50)

class AuthorizeSerializer(serializers.Serializer):
    idTag = serializers.CharField(max_length=255)

class StartTransactionSerializer(serializers.Serializer):
    connectorId = serializers.CharField(max_length=255)
    idTag = serializers.CharField(max_length=255)
    timestamp = serializers.DateTimeField()
    meterStart = serializers.FloatField()

class StopTransactionSerializer(serializers.Serializer):
    transactionId = serializers.IntegerField()
    timestamp = serializers.DateTimeField()
    meterStop = serializers.FloatField()


class TransactionSerializer(serializers.ModelSerializer):
    connector_charger_name = serializers.SerializerMethodField()
    connector_tag_name = serializers.SerializerMethodField()

    class Meta:
        model = Transaction
        fields = '__all__'

    def get_connector_charger_name(self, obj):
        return obj.connector.charger.name

    def get_connector_tag_name(self, obj):
        return obj.connector.tag_name


class ChargerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Charger
        fields = '__all__'