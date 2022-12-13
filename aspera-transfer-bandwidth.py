#!/usr/bin/python2.7

## Thomas HERBIN
## 2/08/2018

## Script to output metric in the "Influxdb line coding" style to feed into telegraf and influxdb
## The scripts feed informations about the current Aspera transfers into Influx

import requests
from datetime import datetime, timedelta
import urllib3
import urllib
import json
import time
import re

import traceback

import sys

reload(sys)
sys.setdefaultencoding('utf8')

## Variables You have to modify, the Hostname is just the console Hostname
user = "monitoring"
password = "REDACTED"
aspera_api = "https://YOURHOSTNAME.FQDN/aspera/console/api"
hostname_shortname = "YOUR_HOSTNAME_SHORTNAME"

## Function to escape space, comma and equal sign for the InfluxDB tags
## https://docs.influxdata.com/influxdb/v1.7/write_protocols/line_protocol_reference/#special-characters
def fn_escape( str ):
 return re.sub(r'(\ |\=|\,)',lambda m:{' ':'\ ','=':'\=',',':'\,'}[m.group()], str);


## Timestamp for the value that will be outputed to influxdb
timestamp = int(round(time.time() * 1000000000))


## Make the warning about not checking the HTTPS certificate silent
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

## Get Current date minus 24 h
yesterday_date = datetime.utcnow() - timedelta(seconds=10)
yesterday_date = yesterday_date.strftime('%Y-%m-%d %H:%M:%S')



payload = {     'from' : yesterday_date,
                'filter1' : 'status',
                'comp1': 'eq',
                'val1': 'running'}

## Add try catch to output meaningfull error to file
try:

        # Setup a session to be able to use Cookies and not need to login every time (doesn't seem to work)
        session = requests.Session()

        # Get list of all transfer that are running only
        response = session.get(aspera_api + '/transfers', verify=False, auth=(user, password), params=payload)
        transfers = response.json()


        transfersID_current = []

        ## Parse through list of all transfers
        for transfer in transfers:
                #print transfer['status']
                #print json.dumps(transfer, indent=4, sort_keys=True)

                #if transfer['status'] == "completed":
                #       transfer_completed += 1
                #elif transfer['status'] == "cancelled":
                #       transfer_cancelled += 1
                #elif transfer['status'] == "error":
                #       transfer_error += 1
                ## Put Current Transfer ID into an array
                if transfer['status'] == "running":
                        transfersID_current.append(transfer['id'])


        ## For every ID of a transfer that's running we want the details to get the Current Bandwidth
        for ID in transfersID_current:
                response = session.get(aspera_api + '/transfers/' + str(ID), auth=(user, password), verify=False)

                transfer_current = response.json()

                #print transfer_current['last_calculated_rate_bps']

                current_rate = transfer_current['last_calculated_rate_bps']

                ## Need to check if the calculated rate is a number (can be 'None' if the api hasn't calculated it yet)
                if current_rate is not None:

                        #print(current_rate)

                        ## If not bytes written, byte loss can only be 0 - Prevent divide by 0
                        percent_lost = 0
                        if transfer_current['bytes_written'] != 0:
                                percent_lost = round(transfer_current['bytes_lost'] / float(transfer_current['bytes_written'] + transfer_current['bytes_lost']), 4)


                        print ("Aspera_Console_Transfer" +

                                # tags
                                ",host=" + hostname_shortname +
                                ",source=" + transfer_current['source'] +
                                ",source_description=" + fn_escape(transfer_current['source_description']) +
                                ",destination=" + transfer_current['destination'] +
                                ",destination_description=" + fn_escape(transfer_current['destination_description']) +

                                ",session_uuid=" + transfer_current['session_uuid'] +
                                ",contact=" + fn_escape(transfer_current['contact']) +
                                ",name="  + fn_escape(transfer_current['name']) +

                                ",target_rate=" + str(transfer_current['target_rate_kbps']) +
                                ",started_via=" + fn_escape(str(transfer_current['started_via'])) +

                                # fields
                                " current_rate=" + str(current_rate) +
                                ",bytes_lost=" + str(transfer_current['bytes_lost']) +
                                ",bytes_written=" + str(transfer_current['bytes_written']) +
                                ",percent_bytes_lost=" + str(percent_lost) +

                                " " + str(timestamp) )


except Exception as e:
        print (e)
        f = open("/tmp/error-aspera.txt", "a")
        f.write(datetime.now().strftime('%Y-%m-%d %H:%M:%S') + " - " + str(e) + "\n")

