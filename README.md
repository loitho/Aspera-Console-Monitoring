# Aspera Console Monitoring

## What is this for ? 
You might be running an Aspera Console System that lets you see the current transfers, the bandwidth used etc ...
This would make you able to send the Aspera Console Data to InfluxDB in that case.

## Requirements 
- Aspera console, tested on *v3.4.2*, but should work on newer versions
- Telegraf (to run the 2 scripts)
- InfluxDB to store the results. (You might be able to reformat the output to whatever TSDB you desire, check the code)

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

