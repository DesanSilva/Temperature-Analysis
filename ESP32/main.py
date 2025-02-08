import network
import machine
import time
import ujson
from umqtt.simple import MQTTClient
import esp32
import ntptime
from sensors import initialize_sensors

#--------------------------------------------------------------------------------------------------------------------------

#mqtt broker (replace the following fields with necessary information)
aws_broker = "" #aws broker address (endpoint)
clientid = "ESP32"
pkey = "/ESP32-private.pem.key"
ccert = "/ESP32-certificate.pem.crt"
rroot_ca = "/AmazonRootCA1.pem"
pub_topic = "sensors"
key=None
cert=None

#--------------------------------------------------------------------------------------------------------------------------

with open(pkey, 'r') as f:
    key = f.read()
with open(ccert, 'r') as f:
    cert = f.read()
with open(rroot_ca, 'r') as f:
    root = f.read()
    
sslp = {"key":key, "cert":cert, "server_side":False}#ssl parameters

wlan=network.WLAN(network.STA_IF)

print('ESP_32 WiFi program')
wlan.active(True)
wlan.connect(ssid,psk)
print("connecting to wifi")
while not wlan.isconnected():
    print(".",end=" ")
    time.sleep(0.5)
    #machine.idle()
print("connceted to wlan {} with ip:{}".format(ssid,wlan.ifconfig()[0]))
ntptime.settime()
time.sleep(1)
    
print("Begin connection with MQTT Broker :: {}".format(aws_broker))
mqtt = MQTTClient(client_id=clientid, server=aws_broker,port=8883,keepalive=1200,ssl=True,ssl_params=sslp)
mqtt.connect()
print("Connected to MQTT  Broker :: {}".format(aws_broker))

#--------------------------------------------------------------------------------------------------------------------------

# Get all sensor objects
temp_sensor, light_sensor, uv_sensor = initialize_sensors()

#--------------------------------------------------------------------------------------------------------------------------

def read_all_sensors():
    try:
        # Read temperature and humidity
        temperature = temp_sensor.read_temperature()
        humidity = temp_sensor.read_humidity()
        
        # Read light an UV intensity
        light_level = light_sensor.read_light()
        uv_level = uv_sensor.read_uv()
        
        return {
            "temperature": temperature,
            "humidity": humidity,
            "light_level": light_level,
            "uv_level": uv_level
        }
    except Exception as e:
        print(f"Error reading sensors: {e}")
        return None

#--------------------------------------------------------------------------------------------------------------------------

while True:
    try:
        readings = read_all_sensors()
        if readings:
            mssg = ujson.dumps(readings)
            mqtt.publish(pub_topic, mssg)
            print(mssg)
            print("-" * 30)
        time.sleep(600)
        
    except KeyboardInterrupt:
        print("Program stopped")
        break
    except Exception as e:
        print(f"Error in main loop: {e}")
        time.sleep(600)

wlan.disconnect()
#machine.reset()
