# Temperature-Analysis
IoT data collection, database storage and retrieval and Analysis of the associations of temperature with humidity, UV intensity and light intensity.\
\
The instructions for use and setup are given below:\
load_data_atlas.py contains the code for maintaining the AWS -> mongoDB connection. should be run on terminal.\
All files inside ESP32 folder need to be inserted into the ESP32.\
ESP32 must be connected to the sensors with the information given below.\
\
<ins>Setup:</ins>
## Sensors -> ESP23 connection pinouts

### <ins>HTU21D - Temperature / Humidity</ins>
VCC -> 3v3\
SCL -> G22\
SDA -> G21\
GND -> GND

### <ins>BH1750 - Light Intensity</ins>
VCC -> 3v3\
SCL -> G17\
SDA -> G16\
GND -> GND

### <ins>GUVA-S12SD - UV level</ins>
VCC -> 3v3\
SIG -> G32\
GND -> GND

## connection details

### <ins>load_atlas_data.py</ins>
MongoDB client connection string\
AWS broker url\
.pem.crt file path in PC\
private.pem.key file path in PC\
rootCA file path in PC

### <ins>ESP32/main.py</ins>
add AWS broker url\
add the WiFi SSID and password to the boot.py file\
replace AWS certificate and rsa private key files, and rename to [AmazonRootCA1.pem, ESP32-certificate.pem.crt, ESP32-private.pem.key]
\
The AWS broker url and the publish topic must be the same in both files.
