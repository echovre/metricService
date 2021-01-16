#!/usr/bin/env python
import os, sys, json
import urllib3
http = urllib3.PoolManager()

#curl -X POST http://127.0.0.1:5000/ -H 'Content-Type: application/json' -d '{"ids":["e3e70682-c209-4cac-629f-6fbed82c07cd", "16a92bf5-0e5d-4372-a801-1d4e2895be65", "4ffaecc0-3047-4da7-abe2-dd4163f17e61"]}'

payload={"ids":["e3e70682-c209-4cac-629f-6fbed82c07cd", "16a92bf5-0e5d-4372-a801-1d4e2895be65", "4ffaecc0-3047-4da7-abe2-dd4163f17e61"]}

APP_URL="https://metricservice.herokuapp.com/"

encoded_data = json.dumps(payload).encode('utf-8')

response = http.request('POST',APP_URL,body=encoded_data,
     headers={'Content-Type': 'application/json'})

print("Got response:")
print(response.data.decode('utf-8'))

