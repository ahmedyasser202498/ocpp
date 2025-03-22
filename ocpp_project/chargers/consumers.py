import json
import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer
from ocpp.routing import on
from ocpp.charge_point import ChargePoint as OcppChargePoint
from ocpp.charge_point import ChargePoint as ChargePoint
from ocpp.exceptions import OCPPError
from channels.layers import get_channel_layer
from datetime import datetime

from .services import ChargerService,ChargingSessionService

class OCPPWebSocketConsumer(AsyncWebsocketConsumer):

    charger_channels = {}


    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['charger_id']
        self.room_group_name = f"ocpp_{self.room_name}"

        if not await ChargerService().authenticate_charger(self.room_name):
            # If charger is not found, reject connection
            await self.close()
            return

        OCPPWebSocketConsumer.charger_channels[self.room_name] = self.channel_name

        # Accept WebSocket connection
        await self.accept()
        self.charge_point = ChargePoint(self.channel_name, self)
        self.connected = True

        await ChargerService().change_charger_status(self.room_name)


    async def disconnect(self, close_code):
        self.connected = False

    async def receive(self, req_data):
        if isinstance(req_data, str):
            req_data = json.loads(req_data )  
        else:
            req_data = req_data

        if req_data['command'] == 'BootNotification':
            await self.handle_boot_notification(req_data)
        elif req_data['command'] == 'Heartbeat':
            await self.handle_heartbeat()
        elif req_data['command'] == 'Authorize':
            await self.handle_authorize(req_data)
        elif req_data['command'] == 'StartTransaction':
            await self.handle_start_transaction(req_data)
        elif req_data['command'] == 'StopTransaction':
            await self.handle_stop_transaction(req_data)
        elif req_data['command'] == 'RemoteStartTransaction':
            await self.handle_remote_start_transaction(req_data)
        elif req_data['command'] == 'RemoteStopTransaction':
            await self.handle_remote_stop_transaction(req_data)
        else:
            await self.handle_custom_action(req_data)

    async def send_json(self, message):
        """Sends JSON message to WebSocket"""
        await self.send(text_data=json.dumps(message))


    async def handle_custom_action(self, message):
        """Handle any other custom actions"""
        response = {
            "status": "Unknown action",
            "currentTime": datetime.utcnow().isoformat(),
        }
        await self.send_json(response)


    ## ACTIONS

    async def handle_boot_notification(self, req_data):
        
        await ChargerService().boot_notification(req_data['charger_name'],req_data['data'])

        response = {
            "status": "Accepted",
            "currentTime": datetime.utcnow().isoformat(),
            "interval": 10
        }
        await self.send_json(response)

    async def handle_heartbeat(self):
        response = {
            "status": "Accepted",
            "currentTime": datetime.utcnow().isoformat(),
        }
        await self.send_json(response)

    async def handle_authorize(self, req_data):
        authorization_status = await ChargerService().authorize(req_data['charger_name'],req_data['data']['idTag'])
        response = {
            "status": authorization_status
        }
        await self.send_json(response)

    
    async def handle_start_transaction(self,req_data):
        transaction_id,error = await ChargingSessionService().start_transaction(req_data['charger_name'],req_data['data'])
        if error:
            response = {
            "status": "Blocked",
            }
        else:
            response = {
                "status": "Accepted",
                "transactionId": transaction_id
            }
        await self.send_json(response)

    async def handle_stop_transaction(self, req_data):
        await ChargingSessionService().stop_transaction(req_data['data'])
        response = {
            "status": "Accepted"
        }
        await self.send_json(response)
    
    async def handle_remote_start_transaction(self, req_data):
        transaction_id = await ChargingSessionService().start_transaction(req_data['charger_name'],req_data['data'], remote=True)
        response = {
            "status": "Accepted",
            "transactionId": transaction_id
        }
        await self.send_json(response)
    
    async def handle_remote_stop_transaction(self, req_data):
        await ChargingSessionService().stop_transaction(req_data['data'])
        response = {
            "status": "Accepted"
        }
        await self.send_json(response)

    
    @classmethod
    async def send_to_charger(cls, charger_name, req_data):
        channel_name = cls.charger_channels.get(charger_name)

        
        if channel_name:
            # Send the message to the charger using its channel_name
            channel_layer = get_channel_layer()
            await channel_layer.send(channel_name, {
                "type": "receive",  # this matches the method name for receiving messages
                "data": req_data['req_data'],
                "charger_name":charger_name,
                "command":req_data['action']
            })