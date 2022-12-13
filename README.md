# Aspera Console Monitoring

## What is this for ? 
You might be running an Aspera Console System that lets you see the current transfers, the bandwidth used etc ...
This would make you able to send the Aspera Console Data to InfluxDB in that case.

## Requirements 
- Aspera console, tested on *v3.4.2*, but should work on newer versions
- Telegraf (to run the 2 scripts)
- Python 2.7
- InfluxDB to store the results. (You might be able to reformat the output to whatever TSDB you desire, check the code)
- Grafana to display the results (Or use any concurrent, doesn't matter)

## How it works
There are 2 Python (2.7, sorry, that was written a long time ago) scripts : 
- aspera-transfer-bandwidth.py
- get-aspera-transfer-stats.py

Those 2 Python Scripts should be run by Telegraf regularly, using the telegraf config *exec_script_aspera.conf* file
This will send data to the output you've chosen in Telegraf, for us it was Influx.

### aspera-transfer-bandwidth.py
Simply get the bandwidth of each individual transfers every 10 seconds

### get-aspera-transfer-stats.py
Get a global status of all transfers to the console every 10 minutes

## Grafana 
### View
This is what it looks like in Grafana when properly Setup: 
![image](https://user-images.githubusercontent.com/1643279/207408010-b85b29a8-33d6-433a-8b39-6bfcf15ac0a8.png)

![image](https://user-images.githubusercontent.com/1643279/207407910-14fb5cd4-37e7-4596-8080-b143435988b4.png)

### Configuration 
- You can import the Grafana Dashboard called *Aspera Console.json* in this repository
- You'll then need to update the Grafana Dashboard Variable called "connect_server", it must be your HighSpeed Transfer Server IP Addresses
  - In this configuration, it's currently setup to `10.42.42.4[1-2]|10.43.43.4[3-4]`, meaning it matches 
    - 10.42.42.41
    - 10.42.42.42
    - 10.43.43.43
    - 10.43.43.44
  - Once Changed, update your dashboard and it should work nicely.
