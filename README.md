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
