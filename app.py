#!/usr/bin/env python
import os, sys, json
import urllib3
from flask import Flask, request, jsonify
app = Flask(__name__)
http = urllib3.PoolManager()

#https://housekeeping.vacasa.io/cleans?filter[id][in]=16a92bf5-0e5d-4372-a801-1d4e2895be65,e3e70682-c209-4cac-629f-6fbed82c07cd

#https://housekeeping.vacasa.io/#tag/cleans

CLEANS_URL='https://housekeeping.vacasa.io/cleans'

def getMetrics(cleansData):
    timesDict={}
    for each in cleansData:
        myId=each['id']
        cleanTime=each['attributes']['predicted_clean_time']
        timesDict[myId]=cleanTime
    
    firstTime=timesDict[list(timesDict.keys())[0]]
    minTime=firstTime
    maxTime=firstTime
    totalTime=0
    count=0

    for each in timesDict:
        cleanTime=timesDict[each]
        totalTime+=cleanTime
        if minTime>cleanTime: minTime=cleanTime 
        if maxTime<cleanTime: maxTime=cleanTime 
        count+=1

    metrics={}
    metrics["maxCleanTime"]=maxTime
    metrics["minCleanTime"]=minTime
    metrics["totalCleanTime"]=totalTime
    metrics["idsCounted"]=count
    return metrics

#http://127.0.0.1:5000/e3e70682-c209-4cac-629f-6fbed82c07cd
@app.route('/<uuid>')
def doMetric(uuid):
    #inputs=["e3e70682-c209-4cac-629f-6fbed82c07cd",
    #"16a92bf5-0e5d-4372-a801-1d4e2895be65",
    #"4ffaecc0-3047-4da7-abe2-dd4163f17e61"];
    #metrics=getMetrics(inputs)
    metrics=getMetrics([uuid])
    return jsonify(metrics)
    
#curl -X POST http://127.0.0.1:5000/ -H 'Content-Type: application/json' -d '{"ids":["e3e70682-c209-4cac-629f-6fbed82c07cd", "16a92bf5-0e5d-4372-a801-1d4e2895be65", "4ffaecc0-3047-4da7-abe2-dd4163f17e61"]}'
@app.route('/', methods=['POST'])
def doMetrics():
    content = request.json
    urlParams="?filter[id][in]="
    #todo error check content[ ids]
    for myId in content['ids']:
        urlParams+=myId
        urlParams+=","
    urlParams=urlParams.rstrip(",") #strip last comma
    myUrl=CLEANS_URL+urlParams
    cleansResponse = http.request('GET', myUrl)
    responseData=json.loads(cleansResponse.data)
    #TODO: error check request
    return getMetrics(responseData['data'])

if __name__ == '__main__':
    app.run(debug=True)
