from machine import Pin, I2C, ADC
import time

class HTU21D:
    def __init__(self, i2c, addr=0x40):
        self.i2c = i2c
        self.addr = addr
        
    def read_temperature(self):
        self.i2c.writeto(self.addr, bytes([0xE3]))
        time.sleep(0.2)
        data = self.i2c.readfrom(self.addr, 3)  # Read 3 bytes
        temp_raw = (data[0] << 8) + data[1]
        temperature = -46.85 + (175.72 * temp_raw / 65536)
        return temperature

    def read_humidity(self):
        self.i2c.writeto(self.addr, bytes([0xE5]))
        time.sleep(0.2)
        data = self.i2c.readfrom(self.addr, 3) # Read 3 bytes
        hum_raw = (data[0] << 8) + data[1]
        hum = -6 + (125 * hum_raw / 65536)
        humidity = max(0, min(100, hum))  # Ensure range 0-100%
        return humidity

class BH1750:
    def __init__(self, i2c, addr=0x23):
        self.i2c = i2c
        self.addr = addr
        # Initialize the sensor in CONTINUOUS_HIGH_RES_MODE
        self.i2c.writeto(self.addr, bytes([0x10]))
        time.sleep(0.180)

    def read_light(self):
        data = self.i2c.readfrom(self.addr, 2)
        light_level = (data[0] << 8 | data[1]) / 1.2
        return light_level

class GUVAS12SD:
    def __init__(self, pin):
        self.adc = ADC(Pin(pin))
        self.adc.atten(ADC.ATTN_11DB)  # Full range: 3.3v

    def read_uv(self):
        raw_value = self.adc.read()
        # Convert ADC reading (0-4095) to voltage (0-3.3V)
        voltage = (raw_value / 4095) * 3.3
        
        # Convert voltage to UV intensity based on sensor sensitivity
        current = voltage / 3.3 * 0.14
        uv_intensity = current * 1000
        return uv_intensity

def initialize_sensors():
    i2c_htu = I2C(0, scl=Pin(22), sda=Pin(21))
    i2c_bh = I2C(1, scl=Pin(17), sda=Pin(16))
    
    # Initialize each sensor with its respective I2C bus
    temp_sensor = HTU21D(i2c_htu)
    light_sensor = BH1750(i2c_bh)
    uv_sensor = GUVAS12SD(32)
    
    return temp_sensor, light_sensor, uv_sensor
