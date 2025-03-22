from .models import Charger,Transaction,StatusLog,Connector
from channels.db import database_sync_to_async
from .choices import ChargerStatus, TransactionStatus, TransactionType, LogStatus, ConnectorStatus

import asyncio
from datetime import datetime,timedelta
import os
import pytz
from django.utils.dateparse import parse_datetime

class ChargerService:

    async def authenticate_charger(self, charger_name):
        """
        Authenticate a charger by checking if it exists in the database.

        :param charger_name: The name of the charger to authenticate (string)
        :return: True if the charger is authenticated, otherwise False
        """
        
        try:
            await database_sync_to_async(Charger.objects.get)(name=charger_name)
            return True
        except Charger.DoesNotExist:
            print(f"Charger with ID {charger_name} not found in the system.",flush=True)
            return False
        

    async def authorize(self, charger_name, id_tag):
        """
        Authorize a user to use a charger by verifying if the ID tag matches.

        :param charger_name: The name of the charger (string)
        :param id_tag: The ID tag of the user attempting to access the charger (string)
        :return: "Accepted" if the ID tag matches, otherwise "Rejected"
        """

        charger = await database_sync_to_async(Charger.objects.get)(name=charger_name)
        if charger.id_tag in id_tag:
            return "Accepted"
        return "Rejected"
    
    async def change_charger_status(self, charger_name):
        """
        Change the status of the charger between "CONNECTED" and "DISCONNECTED".
        The last communication timestamp is also updated.

        :param charger_name: The name of the charger whose status needs to be changed (string)
        :return: None
        """

        charger = await database_sync_to_async(Charger.objects.get)(name=charger_name)
        
        new_status = ChargerStatus.DISCONNECTED if charger.status == ChargerStatus.CONNECTED else ChargerStatus.CONNECTED
        charger.status = new_status
        charger.last_communication=datetime.now()
        await database_sync_to_async(charger.save)()
    
    async def create_status_log(self, charger_name,status=LogStatus.ERROR):
        """
        Create a status log entry for the charger with the given status and timestamp.
        The default status is ERROR.

        :param charger_name: The name of the charger (string)
        :param status: The status to be recorded (default is LogStatus.ERROR)
        :return: None
        """

        charger = await database_sync_to_async(Charger.objects.get)(name=charger_name)
        database_sync_to_async(StatusLog.objects.create)(charger=charger,timestamp=datetime.now(),status=status)


    def calculate_energy_consumed_kWh(start_time, end_time):
        """
        Calculate energy consumed in kWh.
        
        :param start_time: The start time of the transaction (datetime)
        :param end_time: The end time of the transaction (datetime)
        :return: Energy consumed in kWh
        """

        utc = pytz.UTC
    
        if start_time.tzinfo is None:
            start_time = utc.localize(start_time)  
            
        if end_time.tzinfo is None:
            end_time = utc.localize(end_time)

        if start_time.tzinfo != end_time.tzinfo:
            end_time = end_time.astimezone(start_time.tzinfo)

        charger_power_kW= float(os.environ.get('CHARGER_POWER_PER_KW'))
        time_diff = end_time - start_time
        time_in_hours = time_diff.total_seconds() / 3600  
        
        energy_consumed = charger_power_kW * time_in_hours
        return energy_consumed
    
    async def boot_notification(self,charger_name,data):
        """
        Update the charger's metadata based on the boot notification data.

        :param charger_name: The name of the charger (string)
        :param data: A dictionary containing the boot notification data (e.g., model, serial numbers)
        :return: None
        """

        charge_box_serial_number = data.get('chargeBoxSerialNumber')
        charge_point_model = data.get('chargePointModel')
        charge_point_serial_number = data.get('chargePointSerialNumber')
        charge_point_vendor = data.get('chargePointVendor')
        firmware_version = data.get('firmwareVersion')
        iccid = data.get('iccid')
        imsi = data.get('imsi')
        meter_serial_number = data.get('meterSerialNumber')

        await database_sync_to_async(Charger.objects.filter(name=charger_name).update)\
        (model=charge_point_model,vendor=charge_point_vendor,box_serial_number=charge_box_serial_number,serial_number=charge_point_serial_number,firmware_version=firmware_version,iccid=iccid,imsi=imsi,meter_serial_number=meter_serial_number)

    def update_transaction(transaction_id, timestamp, energy_consumed, meter_stop):
        """
        Update the transaction with the provided data: end time, energy consumed, and meter stop value.
        Marks the transaction as "COMPLETED".

        :param transaction_id: The ID of the transaction to update (integer)
        :param timestamp: The end time of the transaction (datetime)
        :param energy_consumed: The total energy consumed during the transaction (float)
        :param meter_stop: The final meter reading (float)
        :return: None
        """

        Transaction.objects.filter(id=transaction_id).update(
            end_time=timestamp,
            energy_consumed_kWh=energy_consumed,
            status=TransactionStatus.COMPLETED,
            meter_stop=meter_stop
        )

    def update_connector(connector_id, timestamp):
        """
        Update the status and last communication time of a connector.
        Sets the status to "AVAILABLE".

        :param connector_id: The ID of the connector to update (integer)
        :param timestamp: The timestamp to set for the last communication (datetime)
        :return: None
        """

        Connector.objects.filter(id=connector_id).update(
            last_communication=timestamp,
            status=ConnectorStatus.AVAILABLE
        )
    def get_connector_id(connector):
        """
        Retrieve the ID of a connector object.

        :param connector: The connector object from which to retrieve the ID
        :return: The ID of the connector (integer)
        """

        return connector.id

    

class ChargingSessionService:
    async def start_transaction(self,charger_name,req_data, remote=False):
        """
        Start a new transaction for the given charger and connector.
        Checks authorization, updates the connector’s status, and creates a new transaction.

        :param charger_name: The name of the charger (string)
        :param req_data: A dictionary containing the request data (e.g., connector ID, meter start, timestamp)
        :param remote: A boolean indicating if the transaction is started remotely (default is False)
        :return: The new transaction ID and a boolean indicating whether the transaction was rejected
        """

        connector_tag = req_data.get('connectorId')
        meter_start = req_data.get('meterStart')
        id_tag = req_data.get('idTag')
        timestamp_str = req_data.get('timestamp')
        timestamp = parse_datetime(timestamp_str)


        result=await ChargerService().authorize(charger_name,id_tag)
        if result == "Rejected":
            return None,True
        charger = await database_sync_to_async(Charger.objects.get)(name=charger_name)

        connector = await database_sync_to_async(Connector.objects.get)(tag_name=connector_tag,charger=charger)
        if remote:
            new_transaction=  await database_sync_to_async(Transaction.objects.create)(connector=connector,start_time=timestamp,meter_start=meter_start,type=TransactionType.REMOTE)
        else:
            new_transaction=  await database_sync_to_async(Transaction.objects.create)(connector=connector,start_time=timestamp,meter_start=meter_start)

        await database_sync_to_async(Connector.objects.filter(charger=charger,tag_name=connector_tag).update)(status=ConnectorStatus.OCCUPIED, last_communication=datetime.now())
        return new_transaction.id,False
    
    async def stop_transaction(self, req_data):
        """
        Stop an ongoing transaction, calculate the energy consumed during the session,
        and update the transaction and connector details.

        :param req_data: A dictionary containing the transaction ID, meter stop, and timestamp
        :return: None
        """

        transaction_id = req_data.get('transactionId')
        meter_stop = req_data.get('meterStop')
        timestamp_str = req_data.get('timestamp')
        timestamp = parse_datetime(timestamp_str)
        
        transaction= await database_sync_to_async(Transaction.objects.get)(id=transaction_id)
        connector_id = ChargerService.get_connector_id(transaction)

        energy_consumed = ChargerService.calculate_energy_consumed_kWh(transaction.start_time, timestamp)

        await database_sync_to_async(ChargerService.update_transaction)(transaction_id, timestamp, energy_consumed, meter_stop)
        await database_sync_to_async(ChargerService.update_connector)(connector_id, timestamp)


class ChargingRequestService:

    def send_command_request(charger_name, command_data):
        """
        Send a command request to the charger using a WebSocket connection.

        :param charger_name: The name of the charger to send the command to (string)
        :param command_data: The data associated with the command to be sent (dictionary)
        :return: None
        """

        from .consumers import OCPPWebSocketConsumer
        asyncio.run(OCPPWebSocketConsumer.send_to_charger(charger_name, command_data))
