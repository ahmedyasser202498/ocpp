# OCPP Backend Module for Electric Vehicle (EV) Chargers

## Introduction

The OCPP Backend Module is designed to facilitate communication between Electric Vehicle (EV) chargers and a backend system using the OCPP 1.6 JSON protocol. The goal of this module is to establish a robust, scalable, and efficient backend solution that supports WebSocket connections, handles incoming OCPP messages, and provides an API for interacting with connected chargers.

This module allows you to:
- Manage charger states
- Monitor charging transactions
- Authorize users for charging sessions via RFID or remote authorization
- Send commands to chargers
- Start and stop charging sessions
- Track energy consumption

## Features

- **WebSocket Communication**: Establish WebSocket connections between EV chargers and the backend for real-time communication using the OCPP 1.6 JSON protocol.
- **Charger Management**: Handle and track the status of connected chargers, including connection states, charger details, and authorization.
- **Charging Sessions**: Start and stop charging sessions, track energy consumption, and log transaction details.
- **Authorization**: Implement RFID and remote user authorization mechanisms for EV chargers.
- **API**: Expose endpoints to list transactions, connected chargers, and send commands to chargers via Django's REST framework.

## Objective

This module simulates the backend for managing and interacting with EV chargers in an OCPP-compliant system. The backend communicates with chargers through WebSocket connections, handling actions such as:
- BootNotification
- Heartbeat
- Authorize
- StartTransaction
- StopTransaction
- And more based on the OCPP 1.6 protocol.

By the end of this exercise, you will have a fully functional Django-based backend that communicates with multiple chargers, tracks charging sessions, and provides an API for integration with external systems.

## Key Technologies

- **Django**: Web framework for building the backend application.
- **Django Channels**: For handling WebSocket connections and asynchronous communication.
- **OCPP Protocol**: Implementation of the Open Charge Point Protocol (OCPP) 1.6 JSON specification for communication with chargers.
- **Django REST Framework**: For building APIs to interact with the backend.
- **JWT Authentication**: For secure API access using JSON Web Tokens.


## Setup Environment and Using Docker Compose

To set up the environment and run the application using Docker Compose, follow these steps:

### Prerequisites
Ensure that you have [Docker](https://www.docker.com/products/docker-desktop) and [Docker Compose](https://docs.docker.com/compose/) installed on your machine.

### Steps to Set Up

1. **Clone the Repository**  
   Clone this repository to your local machine:
   ```bash
   git clone https://github.com/ahmedyasser202498/ocpp
   cd ocpp_project
	```
2. **Build the Docker Containers**  
   To build the Docker images defined in the docker-compose.yml file, run:
   ```bash
   docker-compose build
   ```

3. **Start the Application with Docker Compose**  
   After building the images, start the services (database, Redis, and the web application) with:
   ```bash
   docker-compose up
   ```
   
   This will:
	- Set up a PostgreSQL database service (db).
	- Set up a Redis service (redis).
	- Build and run the web application (web), including migrations and initializing required data.

4. **Access the Web Application**  
   Once the services are up, you can access the web application at http://localhost:8000

5. **Stopping the Services**  
   To stop the services, use:
   ```bash
   docker-compose down

6. **Additional setup**  
   In the docker you will find that we:
	- Initializes charger data in the database, ensuring necessary charger records are created.
		```bash
   		python manage.py create_chargers
		```
		- please use one of the three charger_names created in connection of a websocket ['charger_1','charger_2','charger_3']
		- each charger has two connectors ['connector_1','connector_1'], please use this names in the APIs requests

	- Creates a default user in the system for authentication and interaction with the application.
		```bash
   		python manage.py create_user
		```
		- you will find that this will generate an access and refresh token, and will be printed in your console after running the services, please use this tokens in the apis requests: example
		```bash
   		JWT Access Token >>>>   eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzQyNTk5Njk2LCJpYXQiOjE3NDI1OTkzOTYsImp0aSI6IjMxNzdmNjNjNmRlYTQ3NjdiM2NjOGE3ZTllNWM5Mjk3IiwidXNlcl9pZCI6MX0.p2kwf___7kTYVdsAAA9rSnhOgQTb9oKSs7ry9MAFTXk

		JWT Refresh Token >>>>   eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzQyNTk5Njk2LCJpYXQiOjE3NDI1OTkzOTYsImp0aSI6IjMxNzdmNjNjNmRlYTQ3NjdiM2NjOGE3ZTllNWM5Mjk3IiwidXNlcl9pZCI6MX0.p2kwf___7kTYVdsAAA9rSnhOgQTb9oKSs7ry9MAFTXk
		```
		- if the access token is expired please use the refresh token in this curl to generate new access token:
		```bash

		curl -X POST http://localhost:8000/api/token/refresh/ \
		-H "Content-Type: application/json" \
		-d '{"refresh": "your-refresh-token-here"}' 
		```


## Models Overview

The application includes several Django models that represent core components of the Electric Vehicle (EV) charging system. These models define the structure of data and relationships between different entities. Below is an overview of the key models:

### Charger Model

The `Charger` model represents a charging station that provides charging services for electric vehicles.

- **Fields:**
  - `name`: A unique name for the charger.
  - `status`: The current status of the charger (e.g., `DISCONNECTED`, `CONNECTED`).
  - `last_communication`: The timestamp of the last communication with the charger.
  - `location`: The physical location of the charger (optional).
  - `model`, `vendor`, `box_serial_number`, `serial_number`: Details about the charger hardware and software.
  - `firmware_version`: The version of the firmware installed on the charger.
  - `iccid`, `imsi`: Identifiers related to the SIM card (optional).
  - `meter_serial_number`: The serial number of the meter attached to the charger.
  - `id_tag`: A unique identifier for the charger, automatically generated if not provided.

- **Methods:**
  - `generate_id_tag()`: Generates a unique ID tag using the `uuid` library.
  - `save()`: Overrides the save method to automatically generate an `id_tag` if it is not already set.

### Connector Model

The `Connector` model represents an individual connector at a charging station, which is responsible for charging a vehicle.

- **Fields:**
  - `charger`: A foreign key linking the connector to a specific charger.
  - `connector_tag`: A unique identifier for the connector.
  - `type`: The type of connector (e.g., Type 1, Type 2, etc.).
  - `status`: The current status of the connector (e.g., `AVAILABLE`, `OCCUPIED`. `FAULTY`).
  - `last_communication`: The timestamp of the last communication from the connector.

### Transaction Model

The `Transaction` model represents a charging session that records the start and stop times, energy consumption, and the status of the transaction.

- **Fields:**
  - `connector`: A foreign key linking the transaction to a specific `Connector`. This represents the connector where the transaction occurred.
  - `start_time`: The timestamp when the transaction started.
  - `end_time`: The timestamp when the transaction ended (optional).
  - `energy_consumed_kWh`: The amount of energy consumed during the transaction in kWh (optional).
  - `meter_start`: The starting meter reading at the beginning of the transaction.
  - `meter_stop`: The ending meter reading at the end of the transaction.
  - `status`: The status of the transaction (e.g., `ACTIVE`, `COMPLETED`, `Failed`).
  - `type`: The type of the transaction (e.g., `CHARGER`, `REMOTE`).

### StatusLog Model

The `StatusLog` model keeps a record of the status updates for a charger, such as maintenance messages or status changes.

- **Fields:**
  - `charger`: A foreign key linking the status log to a specific charger.
  - `timestamp`: The timestamp when the status change occurred.
  - `status`: The status value indicating the charger’s condition (e.g., `DISCONNECTED`, `CONNECTED`, `Error`).
  - `message`: An optional message providing additional details about the status change.

---

### Relationships Between Models

- **Charger and Connector**: A `Charger` can have multiple `Connectors`, each representing a physical port where a vehicle can plug in to charge.
- **Charger and Transaction**: A `Connector` can have multiple `Transactions`, each representing a charging session.
- **Charger and StatusLog**: A `Charger` can have multiple `StatusLogs`, which track status updates for the charger.

These models collectively enable the tracking of chargers, their connectors, the charging transactions, and status updates in an EV charging system.



## API Endpoints

The following API endpoints are available for interacting with the Electric Vehicle (EV) charging system:

### 1. **Send Command to system**

- **Endpoint:** `POST /api/chargers/{charger_name}/send-command/`
- **Description:** This endpoint allows sending a command to a specified charger. The request must contain a valid command, and the charger name is specified in the URL path.
- **Permissions:** Requires authentication (`IsAuthenticated`). [**use the access token as bearer token**]
- **Request Body:**
  - `command`: The command to be sent to the charger (e.g., "START", "STOP", etc.).
- **Response:**
  - **200 OK**: If the command is successfully sent to the charger.
  - **400 Bad Request**: If the request body is invalid or the command is not recognized.
  
**Example comands:**

#### 1. **Boot Notification Command**

- **Action:** `BootNotification`
- **Description:** This command notifies the OCPP server that a charger (charging station) is starting up. It provides details about the charger’s serial number, model, vendor, firmware version, and other related data.

**Request Example:**

```json
{
    "command": {
        "action": "BootNotification",
        "req_data": {
            "chargeBoxSerialNumber": "12345ABC",
            "chargePointModel": "Model-X",
            "chargePointSerialNumber": "67890DEF",
            "chargePointVendor": "VendorXYZ",
            "firmwareVersion": "1.2.3",
            "iccid": "89012345678901234567",
            "imsi": "310260123456789",
            "meterSerialNumber": "1122334455"
        }
    }
}
```
- Explanation: This sends a boot notification to the server with the charge point's serial number, model, vendor, and additional data, such as firmware and meter information.

#### 2. **Heartbeat Command**

- **Action:** `Heartbeat`
- **Description:** This command is sent periodically by the charger to the OCPP server to check the connection's health. It confirms that the charger is still alive and operational.

**Request Example:**

```json
{
    "command": {
        "action": "Heartbeat",
        "req_data": {}
    }
}
```
- Explanation: This sends a heartbeat to the server with no additional data. It's simply used to verify that the charger is still functioning and connected.


#### 3. **Authorize Command**

- **Action:** `Authorize`
- **Description:** This command is used to authorize a user for charging based on their RFID card or a specific ID tag. It sends the ID tag data to the server for validation.

**Request Example:**

```json
{
    "command": {
        "action": "Authorize",
        "req_data": {
            "idTag": "1234567890AB"
        }
    }
}
```
- Explanation: This command sends an ID tag (e.g., from an RFID card) to the server to authorize a charging session for the user identified by this ID tag.


#### 4. **Start Transaction Command**

- **Action:** `StartTransaction`
- **Description:** This command is sent when a charging session starts, providing the meter start value and the connector that the user will use to charge.

**Request Example:**

```json
{
    "command": {
        "action": "StartTransaction",
        "req_data": {
            "connectorId": 1,
            "idTag": "e0607b18-2f62-4621-8f4f-ceb6c002e2e0",
            "timestamp": "2025-03-22T12:00:00Z",
            "meterStart": 1000
        }
    }
}
```
- Explanation: This command starts the charging session for a user, providing the ID tag, connector used, start time, and initial meter reading.


#### 5. **Stop Transaction Command**

- **Action:** `StopTransaction`
- **Description:** This command is used to stop a charging session, logging the meter stop value and the total energy consumed during the session.

**Request Example:**

```json
{
    "command": {
        "action": "StopTransaction",
        "req_data": {
            "transactionId": 1,
            "timestamp": "2025-03-22T14:00:00Z",
            "meterStop": 1050
        }
    }
}
```
- Explanation: This command stops the charging session, providing the transaction ID, stop time and final meter reading during the session.


#### 6. **Start Remote Transaction Command**

- **Action:** `StartRemoteTransaction`
- **Description:** This command is sent Remotely to start a charging session, providing the meter start value and the connector that the user will use to charge.

**Request Example:**

```json
{
    "command": {
        "action": "StartRemoteTransaction",
        "req_data": {
            "connectorId": 1,
            "idTag": "1234567890AB",
            "timestamp": "2025-03-22T12:00:00Z",
            "meterStart": 1000
        }
    }
}
```
- Explanation: This command starts the charging session for a user, providing the ID tag, connector used, start time, and initial meter reading.


#### 7. **Stop Remote Transaction Command**

- **Action:** `StopRemoteTransaction`
- **Description:** This command is sent Remotely to stop a charging session,, logging the meter stop value.

**Request Example:**

```json
{
    "command": {
        "action": "StopRemoteTransaction",
        "req_data": {
            "transactionId": 1,
            "timestamp": "2025-03-22T14:00:00Z",
            "meterStop": 1050,
        }
    }
}
```
- Explanation: This command stops the charging session, providing the transaction ID, stop time and final meter reading during the session.