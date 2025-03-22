from django.core.management.base import BaseCommand
from chargers.models import Charger, Connector
from datetime import datetime

class Command(BaseCommand):
    help = 'Create three sample chargers'

    def handle(self, *args, **kwargs):

        charger_data = [
            {
                'name': 'charger_1',
                'status': 'DISCONNECTED',
                'last_communication': datetime.now(),
                'location': 'Tagmo3',
            },
            {
                'name': 'charger_2',
                'status': 'CONNECTED',
                'last_communication': datetime.now(),
                'location': 'Zayed',
            },
            {
                'name': 'charger_3',
                'status': 'DISCONNECTED',
                'last_communication': datetime.now(),
                'location': 'Shrouk',
            },
        ]

        # Create and save chargers
        for charger in charger_data:
            if Charger.objects.filter(name=charger['name']):
                continue
            charger_obj=Charger.objects.create(**charger)

            Connector.objects.create(charger=charger_obj,tag_name='connector_1')
            Connector.objects.create(charger=charger_obj,tag_name='connector_2')
        
        print('Successfully created chargers',flush=True)
