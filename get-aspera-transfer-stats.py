#!/usr/bin/python2.7

## Thomas HERBIN
## 2/10/2018

## Script to output metric in the "Influxdb lince coding" style to feed into telegraf and influxdb
## This script focus on retrieving the amount of transfers in the last 10 minutes
## This script is supposed to be run by telegraf every 10 minutes

import requests
from datetime import datetime, timedelta
import urllib3
import urllib
import json
import time
import re
import sys

## Corrects UTF8 problems
reload(sys)
sys.setdefaultencoding('utf8')

## Variables to Modify to fit your configuration
user = "monitoring"
password = "REDACTED"
aspera_api = "https://YOURHOSTNAME.FQDN/aspera/console/api"
hostname_shortname = "YOURCONSOLEHOSTNAME_SHORTNAME"

## Function to escape space, comma and equal sign for the InfluxDB tags
## https://docs.influxdata.com/influxdb/v1.7/write_protocols/line_protocol_reference/#special-characters
def fn_escape( str ):
 return re.sub(r'(\ |\=|\,)',lambda m:{' ':'\ ','=':'\=',',':'\,'}[m.group()], str);


## Timestamp for the value that will be outputed to influxdb
timestamp = int(round(time.time() * 1000000000))


## Make the warning about not checking the HTTPS certificate silent
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

## Get Current date minus 10 minutes
previous_10m = datetime.utcnow() - timedelta(minutes=10)
previous_10m = previous_10m.strftime('%Y-%m-%d %H:%M:%S')


payload = {     'from' : previous_10m }

# Get list of all transfer , do not verify SSL cert
# https://developer.asperasoft.com/web/console/all#jump5
response = requests.get(aspera_api + '/transfers', verify=False, auth=(user, password), params=payload)
transfers = response.json()

#print json.dumps(transfers, indent=4, sort_keys=True)

## Parse through list of all transfers
try:
        for transfer in transfers:

                print ("Aspera_Console_overview" +

                # tags
                ",host=" + hostname_shortname +
                ",source=" + transfer['source'] +
                ",destination=" + transfer['destination'] +

                ",contact=" + fn_escape(transfer['contact']) +
                ",name="  + fn_escape(transfer['name']) +
                ",id="  + str(transfer['id']) +
                ",status="  + fn_escape(transfer['status']) +

                ",started_via=" + fn_escape(str(transfer['started_via'])) +

                # fields
                # Dummy is so that we can count it
                " bytes_written=" + str(transfer['bytes_written']) +
                ",dummy=1" +

                " " + str(timestamp) )


except Exception as e:
        print (e)
        f = open("/tmp/error-aspera-stats.txt", "a")
        f.write(datetime.now().strftime('%Y-%m-%d %H:%M:%S') + " - " + str(e) + "\n")
