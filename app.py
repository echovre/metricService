#!/usr/bin/env python
import os, sys, json
import urllib3
from flask import Flask, request, jsonify, Response
app = Flask(__name__)
http = urllib3.PoolManager()

CLEANS_URL="https://housekeeping.vacasa.io/cleans"
FILTER_ENDPOINT="?filter[id][in]="

def hasCleanTime(element):
    return 'attributes' in element and 'predicted_clean_time' in element['attributes']

def hasIdField(content):
    return content.get("ids") is not None
    
def validateJsonData(content):
    try:
        responseData=json.loads(content)
        if 'data' not in responseData:
            return False,None
        return True,responseData
    except ValueError:
        return False,None

def getMetrics(cleansData):
    #track number of entries with no clean time
    noCleanTime=0;

    #build dict
    myDict={}
    for each in cleansData:
        myId=each['id']
        if hasCleanTime(each):
            cleanTime=each['attributes']['predicted_clean_time']
        else:
            noCleanTime+=1
        myDict[myId]=cleanTime

    #return metrics
    totalTime=sum(myDict.values())
    minTime=min(myDict.values())
    maxTime=max(myDict.values())
    count=len(cleansData)
    return {"minCleanTime":minTime,
            "maxCleanTime":maxTime,
            "totalCleanTime":totalTime,
            "idsCounted":count,
            "entriesWithNoCleanTime":noCleanTime
           }

@app.route('/', methods=['POST'])
def doMetrics():
    content = request.json

    #validate input
    if not hasIdField(content):
        return Response("ERROR: Received input json with no id field",status=400)

    #build request
    urlParams=FILTER_ENDPOINT
    for myId in content['ids']:
        urlParams += myId + ","
    urlParams=urlParams.rstrip(",") #strip last comma
    
    #make request
    cleansResponse = http.request('GET', CLEANS_URL+urlParams)

    #validate response and get metrics
    valid,response = validateJsonData(cleansResponse.data)
    if not valid:
        return Response("ERROR: Received invalid json response from Vacasa endpoint",status=400)
    else:
        return getMetrics(response['data'])

if __name__ == '__main__':
    app.run(debug=True)
