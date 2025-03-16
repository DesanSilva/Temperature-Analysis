from config import WIFI_SSID, WIFI_PASSWORD
import machine
import time
import ntptime
import network

from umqtt.simple import MQTTClient
from config import CLIENT_ID, AWS_IOT_ENDPOINT, PATH_TO_CERTIFICATE, PATH_TO_PRIVATE_KEY, PATH_TO_AMAZON_ROOT_CA_1

#------------------------------------------------------------------------------
def connect_wifi():
    try:
        wlan = network.WLAN(network.STA_IF)
        print('ESP_32 WiFi program')
        wlan.active(True)
        wlan.connect(WIFI_SSID, WIFI_PASSWORD)
        print("connecting to wifi")
        
        max_attempts = 10
        attempt = 0
        while not wlan.isconnected():
            print(".", end=" ")
            time.sleep(0.5)
            attempt += 1
            if attempt >= max_attempts:
                raise OSError("Failed to connect to WiFi within the allowed time")
        
        print("connected to wlan {} with ip:{}".format(WIFI_SSID, wlan.ifconfig()[0]))
        ntptime.settime()
        time.sleep(1)
    
    except OSError as e:
        print("Caught an OSError:", e)
        print("Stopping the program due to WiFi internal error.")
        machine.reset()
    
        
#------------------------------------------------------------------------------        
def disconnect_wifi():
    network.WLAN(network.STA_IF).disconnect()

#------------------------------------------------------------------------------
def MQTTclient():
    try:
        with open(PATH_TO_PRIVATE_KEY, 'r') as f:
            key = f.read()
        with open(PATH_TO_CERTIFICATE, 'r') as f:
            cert = f.read()
        with open(PATH_TO_AMAZON_ROOT_CA_1, 'r') as f:
            root = f.read()
        
        sslp = {"key":key, "cert":cert, "server_side":False}
    
        print("Begin connection with MQTT Broker :: {}".format(AWS_IOT_ENDPOINT))
        mqtt_client = MQTTClient(client_id=CLIENT_ID, server=AWS_IOT_ENDPOINT,port=8883,keepalive=1200,ssl=True,ssl_params=sslp)
        return mqtt_client
    
    except OSError as e:
        print(f"Error: Network or MQTT connection failed - {e}")
        return None

    except Exception as e:
        print(f"Unexpected error during MQTT connection: {e}")
        return None