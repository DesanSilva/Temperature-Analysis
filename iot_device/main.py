from connection import MQTTclient
from sensors import initialize_sensors, read_sensors
from config import PUB_TOPIC
import random
import time

def main():
    
    mqtt_client = MQTTclient()
    mqtt_client.connect()
    
    temp_sensor, light_sensor, uv_sensor = initialize_sensors()
    
    while True:
        try:
            message = read_sensors(temp_sensor, light_sensor, uv_sensor)
            if message:
                mqtt_client.publish(PUB_TOPIC, message)
                print(message)
            time.sleep(random.uniform(5, 20))
        
        except KeyboardInterrupt:
            print("Program stopped")
            return None
        
        except Exception as e:
            print(f"Error in main loop: {e}")
            time.sleep(2)

# disconnect_wifi()
# machine.reset()

if __name__ == "__main__":
    main()