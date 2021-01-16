#!/usr/bin/env python
import os, sys, json
import urllib3
from flask import Flask, request, jsonify
app = Flask(__name__)

#for now, load everything into memory. Not sure if Im supposed to re-query the list every time or store in some database if the list is big
#(also, heroku apps have 30 sec timeout unless I want to go through the trouble of setting up background jobs)

#not sure how to interpret the parameters list at:
#https://housekeeping.vacasa.io/#tag/cleans
#also seems to return forbidden?:
#https://housekeeping.vacasa.io/#tag/clean_times

CLEANS_URL='https://housekeeping.vacasa.io/cleans'

http = urllib3.PoolManager()
response = http.request('GET', CLEANS_URL)
responseData=json.loads(response.data)

timesDict={}
for each in responseData['data']:
    id=each['id']
    time=each['attributes']['predicted_clean_time']
    timesDict[id]=time

def getMetrics(idsList):
    firstTime=timesDict[list(timesDict.keys())[0]]
    minTime=firstTime
    maxTime=firstTime
    totalTime=0
    count=0

    for each in idsList:
        if each in timesDict:
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
    
    #TODO: error check uuid
    metrics=getMetrics([uuid])
    return jsonify(metrics)
    
#curl -X POST http://127.0.0.1:5000/ -H 'Content-Type: application/json' -d '{"ids":["e3e70682-c209-4cac-629f-6fbed82c07cd", "16a92bf5-0e5d-4372-a801-1d4e2895be65", "4ffaecc0-3047-4da7-abe2-dd4163f17e61"]}'
@app.route('/', methods=['POST'])
def doMetrics():
    #TODO: error check request
    content = request.json
    return getMetrics(content['ids'])

if __name__ == '__main__':
    app.run(debug=True)
