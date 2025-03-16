import logging
from dotenv import load_dotenv, find_dotenv
import os
from os.path import join, dirname
import pymongo as pym

from awscrt import io, mqtt, auth, http
from awsiot import mqtt_connection_builder

import threading
import uuid
import json
import time

#---------------------------------------------------------------------------------------------------

# Configure logging
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - [%(threadName)s]: %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('mqtt_connection.log')
    ]
)

#---------------------------------------------------------------------------------------------------

load_dotenv(find_dotenv("../.env"))

# MongoDB Configuration
mongodb_url = os.getenv("MONGODB_URL")
myclient = pym.MongoClient(mongodb_url) # mongodbconnection string
mydb = myclient["project"] #database name
sensor_data = mydb["sensor_data"] #collection name

# AWS Configuration
ENDPOINT = os.getenv("AWS_IOT_ENDPOINT") #aws broker url
PATH_TO_CERTIFICATE = join(dirname(__file__), "certificates/ESP32-certificate.pem.crt") #.pem.crt
PATH_TO_PRIVATE_KEY = join(dirname(__file__), "certificates/ESP32-private.pem.key") #private.pem.key
PATH_TO_AMAZON_ROOT_CA_1 = join(dirname(__file__), "certificates/AmazonRootCA1.pem") #root ca

#---------------------------------------------------------------------------------------------------

# MQTT Connection Management
class MQTTConnectionManager:
    def __init__(self, endpoint, cert_path, private_key_path, ca_path):
        self.endpoint = endpoint
        self.cert_path = cert_path
        self.private_key_path = private_key_path
        self.ca_path = ca_path
        
        self.mqtt_connection = None
        self.connection_lock = threading.Lock()
        self.is_connected = threading.Event()
        
        self.max_retry_time = 60  # Maximum wait between retries
        self.base_retry_time = 1  # Initial retry time

    def _create_connection(self):
        try:
            event_loop_group = io.EventLoopGroup(1)
            host_resolver = io.DefaultHostResolver(event_loop_group)
            client_bootstrap = io.ClientBootstrap(event_loop_group, host_resolver)

            mqtt_connection = mqtt_connection_builder.mtls_from_path(
                endpoint=self.endpoint,
                cert_filepath=self.cert_path,
                pri_key_filepath=self.private_key_path,
                client_bootstrap=client_bootstrap,
                ca_filepath=self.ca_path,
                client_id=f"ESP32_{uuid.uuid4().hex[:8]}",
                clean_session=False,
                keep_alive_secs=45,
                ping_timeout_ms=5000  # Timeout for ping responses
            )
            return mqtt_connection
        except Exception as e:
            logging.error(f"Connection creation failed: {e}")
            return None

    def connect(self):
        retry_time = self.base_retry_time

        while not self.is_connected.is_set():
            try:
                with self.connection_lock:
                    self.mqtt_connection = self._create_connection()
                    
                    if not self.mqtt_connection:
                        raise Exception("Failed to create MQTT connection")

                    connect_future = self.mqtt_connection.connect()
                    connect_future.result(timeout=10)  # 10-second connection timeout

                    # Subscribe to topic
                    subscribe_future, _ = self.mqtt_connection.subscribe(
                        topic="sensors",
                        qos=mqtt.QoS.AT_LEAST_ONCE,
                        callback=self.on_message_received
                    )
                    subscribe_future.result(timeout=5)

                    self.is_connected.set()
                    logging.info(f"Connected successfully")
                    retry_time = self.base_retry_time  # Reset retry time on successful connection

            except Exception as e:
                logging.warning(f"Connection attempt failed: {e}")
                logging.warning(f"Retrying in {retry_time} seconds...")
                
                time.sleep(retry_time)
                retry_time = min(retry_time * 2, self.max_retry_time)

    def on_message_received(self, topic, payload, **kwargs):
        try:
            payload_str = payload.decode('utf-8')
            data_dict = json.loads(payload_str)
            
            logging.info(f"Received message on {topic}: {data_dict}")
            
            insert_data = {
                "temperature": data_dict.get('temperature', None),
                "humidity": data_dict.get('humidity', None),
                "light_level": data_dict.get('light_level', None),
                "uv_level": data_dict.get('uv_level', None),
                "raw_data": data_dict  # Store full original message for reference
            }
            
            # Ensuring valid data before insertion
            required_fields = ['temperature', 'humidity', 'light_level', 'uv_level']
            missing_fields = {field: insert_data.get(field) for field in required_fields if insert_data.get(field) is None}
            if not missing_fields:
                result = sensor_data.insert_one(insert_data)
                logging.info(f"Inserted document ID: {result.inserted_id}")
            else:
                logging.warning("Missing one or more required data fields")
      
        except Exception as e:
            logging.error(f"Message processing error: {e}")

#---------------------------------------------------------------------------------------------------

def main():
    connection_manager = MQTTConnectionManager(
        ENDPOINT, 
        PATH_TO_CERTIFICATE, 
        PATH_TO_PRIVATE_KEY, 
        PATH_TO_AMAZON_ROOT_CA_1
    )
    
    connection_thread = threading.Thread(target=connection_manager.connect, daemon=True)
    connection_thread.start()

    try:
        # Keep main thread alive
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logging.info("Stopping MQTT connection...")

#---------------------------------------------------------------------------------------------------

if __name__ == "__main__":
    main()