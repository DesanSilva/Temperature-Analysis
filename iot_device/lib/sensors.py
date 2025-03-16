from machine import Pin, I2C, ADC
import time
import ujson

#------------------------------------------------------------------------------
class HTU21D:
    def __init__(self, i2c, addr=0x40):
        self.i2c = i2c
        self.addr = addr
        
    def read_temperature(self):
        self.i2c.writeto(self.addr, bytes([0xE3]))
        time.sleep(0.2)
        data = self.i2c.readfrom(self.addr, 3)
        temp_raw = (data[0] << 8) + data[1]
        temperature = -46.85 + (175.72 * temp_raw / 65536)
        return temperature

    def read_humidity(self):
        self.i2c.writeto(self.addr, bytes([0xE5]))
        time.sleep(0.2)
        data = self.i2c.readfrom(self.addr, 3)
        hum_raw = (data[0] << 8) + data[1]
        hum = -6 + (125 * hum_raw / 65536)
        humidity = max(0, min(100, hum))
        return humidity

#------------------------------------------------------------------------------
class BH1750:
    def __init__(self, i2c, addr=0x23):
        self.i2c = i2c
        self.addr = addr
        self.i2c.writeto(self.addr, bytes([0x10]))  # CONTINUOUS_HIGH_RES_MODE
        time.sleep(0.180)

    def read_light(self):
        data = self.i2c.readfrom(self.addr, 2)
        light_level = (data[0] << 8 | data[1]) / 1.2
        return light_level
        
#------------------------------------------------------------------------------
class GUVAS12SD:
    def __init__(self, pin):
        self.adc = ADC(Pin(pin))
        self.adc.atten(ADC.ATTN_11DB)

    def read_uv(self, calibration_factor=46):
        raw_value = self.adc.read()
        voltage = (raw_value / 4095) * 3.3
        current_nA = (voltage / 10.0) * 1000
        uv_intensity = current_nA / 113.0 * calibration_factor
        return uv_intensity
        
#------------------------------------------------------------------------------
def initialize_sensors():
    try:
        i2c_htu = I2C(0, scl=Pin(22), sda=Pin(21))
        i2c_bh = I2C(1, scl=Pin(17), sda=Pin(16))
    
        temp_sensor = HTU21D(i2c_htu)
        light_sensor = BH1750(i2c_bh)
        uv_sensor = GUVAS12SD(32)
    
        return temp_sensor, light_sensor, uv_sensor
    
    except KeyboardInterrupt:
        print("Program stopped")
        return None
        
    except Exception as e:
        print(f"Error initializing sensors: {e}")
        return None
#------------------------------------------------------------------------------
def read_sensors(temp_sensor, light_sensor, uv_sensor):
    try:
        temperature = temp_sensor.read_temperature()
        humidity = temp_sensor.read_humidity()
        light_level = light_sensor.read_light()
        uv_level = uv_sensor.read_uv()
        
        readings = {
            "temperature": temperature,
            "humidity": humidity,
            "light_level": light_level,
            "uv_level": uv_level
        }
        
        message = ujson.dumps(readings)
        return message
    
    except Exception as e:
        print(f"Error reading sensors: {e}")
        return None