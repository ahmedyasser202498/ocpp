from django.db import models

class ChargerStatus(models.TextChoices):
    DISCONNECTED = 'Disconnected'
    CONNECTED = 'Connected'

class ConnectorStatus(models.TextChoices):
    AVAILABLE = 'AVAILABLE'
    OCCUPIED = 'OCCUPIED'
    FAULTY = 'FAULTY'

class TransactionStatus(models.TextChoices):
    ACTIVE = 'Active'
    COMPLETED = 'Completed'
    FAILED = 'Failed'

class TransactionType(models.TextChoices):
    REMOTE = 'Remote'
    CHARGER = 'Charger'

class LogStatus(models.TextChoices):
    DISCONNECTED = 'Disconnected'
    CONNECTED = 'Connected'
    ERROR = 'Error'