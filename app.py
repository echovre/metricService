#!/usr/bin/env python
import os, sys, json
import urllib3
from flask import Flask, request, jsonify, Response
app = Flask(__name__)
http = urllib3.PoolManager()


CLEANS_URL="https://housekeeping.vacasa.io/cleans"
FILTER_ENDPOINT="?filter[id][in]="
#Note: Seems like we ought to use something like:
#https://housekeeping.vacasa.io/cleans?fields[clean]="predicted_clean_time"
#to minimize the amount of data we need to receive
#but this returns the same as the filter endpoint above
#the filter verb makes more sense to me so ill go with that

#https://housekeeping.vacasa.io/#tag/cleans
#https://housekeeping.vacasa.io/cleans?filter[id][in]=16a92bf5-0e5d-4372-a801-1d4e2895be65,e3e70682-c209-4cac-629f-6fbed82c07cd

def getMetrics(cleansData):
    noIds=0;
    noCleanTime=0;
    timesDict={}
    
    totalTime=0
    count=0
    firstFlag=True
    for each in cleansData:
        #myId=each['id']
        #cleanTime=each['attributes']['predicted_clean_time']
        # do this^ but with some error checking
        if('id' in each):
            myId=each['id']
        else:
            noIds+=1
            continue
        if('attributes' in each and 'predicted_clean_time' in each['attributes']):
            cleanTime=each['attributes']['predicted_clean_time']
        else:
            noCleanTimes+=1
            continue
        timesDict[myId]=cleanTime
        if firstFlag:
            firstTime=minTime=maxTime = cleanTime
            firstFlag=False
            
        #gather metrics
        totalTime+=cleanTime
        if minTime>cleanTime: minTime=cleanTime 
        if maxTime<cleanTime: maxTime=cleanTime 
        count+=1

    #build output dict
    metrics={}
    metrics["maxCleanTime"]=maxTime
    metrics["minCleanTime"]=minTime
    metrics["totalCleanTime"]=totalTime
    metrics["idsCounted"]=count
    metrics["entriesWithNoIds"]=noIds
    metrics["entriesWithNoCleanTime"]=noCleanTime
    return metrics
    

"""
#http://127.0.0.1:5000/e3e70682-c209-4cac-629f-6fbed82c07cd
@app.route('/<uuid>')
def doMetric(uuid):
    #inputs=["e3e70682-c209-4cac-629f-6fbed82c07cd",
    #"16a92bf5-0e5d-4372-a801-1d4e2895be65",
    #"4ffaecc0-3047-4da7-abe2-dd4163f17e61"];
    #metrics=getMetrics(inputs)
    metrics=getMetrics([uuid])
    return jsonify(metrics)
"""
    
#curl -X POST http://127.0.0.1:5000/ -H 'Content-Type: application/json' -d '{"ids":["e3e70682-c209-4cac-629f-6fbed82c07cd", "16a92bf5-0e5d-4372-a801-1d4e2895be65", "4ffaecc0-3047-4da7-abe2-dd4163f17e61"]}'
@app.route('/', methods=['POST'])
def doMetrics():
    #get/check json that was passed
    content = request.json
    text = content.get("ids",None)
    if text is None: return Response("ERROR: Received invalid json",status=400)
    
    #build request
    urlParams=FILTER_ENDPOINT
    for myId in content['ids']:
        urlParams+=myId
        urlParams+=","
    urlParams=urlParams.rstrip(",") #strip last comma
    
    #make request
    cleansResponse = http.request('GET', CLEANS_URL+urlParams)
    #TODO: pull this into its own isJson() function?
    try:
        responseData=json.loads(cleansResponse.data)
    except ValueError:
        return Response("ERROR: Received invalid json response from Vacasa endpoint",status=400)

    #do metrics calc
    return getMetrics(responseData['data'])

if __name__ == '__main__':
    app.run(debug=True)
