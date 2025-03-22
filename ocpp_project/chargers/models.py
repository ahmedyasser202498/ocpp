from django.db import models
from .choices import ChargerStatus, TransactionStatus, TransactionType, LogStatus, ConnectorStatus

import uuid

class Charger(models.Model):
    name = models.CharField(max_length=255, unique=True)
    status = models.CharField(max_length=50, choices=ChargerStatus.choices, default=ChargerStatus.DISCONNECTED)
    last_communication = models.DateTimeField(auto_now=True)
    location = models.CharField(max_length=255, blank=True, null=True)


    model = models.CharField(max_length=100, blank=True, null=True)
    vendor = models.CharField(max_length=100, blank=True, null=True)
    box_serial_number = models.CharField(max_length=100, blank=True, null=True)
    serial_number = models.CharField(max_length=100, blank=True, null=True)
    firmware_version = models.CharField(max_length=50, blank=True, null=True)
    iccid = models.CharField(max_length=20, blank=True, null=True)
    imsi = models.CharField(max_length=20, blank=True, null=True)
    meter_serial_number = models.CharField(max_length=50, blank=True, null=True)
    id_tag = models.CharField(max_length=255, unique=True, blank=True, null=True)

    def generate_id_tag(self):
        return str(uuid.uuid4())
    
    def save(self, *args, **kwargs):
        if not self.id_tag:
            self.id_tag = self.generate_id_tag()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Charger {self.name}"

class Connector(models.Model):
    charger = models.ForeignKey(Charger, on_delete=models.CASCADE, related_name='connectors')
    tag_name = models.CharField(max_length=100)
    type = models.CharField(max_length=50)
    status = models.CharField(max_length=50, choices=ConnectorStatus.choices, default=ConnectorStatus.AVAILABLE)
    last_communication = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Connector {self.tag_name} for Charger {self.charger.name}"
    

class Transaction(models.Model):
    connector = models.ForeignKey(Connector, related_name='transactions', on_delete=models.CASCADE)
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    energy_consumed_kWh = models.FloatField(null=True, blank=True)
    meter_start = models.FloatField(null=True, blank=True)
    meter_stop = models.FloatField(null=True, blank=True)
    status = models.CharField(max_length=50, choices=TransactionStatus.choices, default=TransactionStatus.ACTIVE)
    type = models.CharField(max_length=50, choices=TransactionType.choices, default=TransactionType.CHARGER)

    def __str__(self):
        return f"Transaction {self.id} for Charger {self.charger.name}"

class StatusLog(models.Model):
    charger = models.ForeignKey(Charger, related_name='status_logs', on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50, choices=LogStatus.choices)
    message = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"StatusLog for Charger {self.charger.name} at {self.timestamp}"
