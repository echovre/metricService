# metricService

## Inputs: The service takes a json object which is a list of ids:
```
{"ids":["e3e70682-c209-4cac-629f-6fbed82c07cd", "16a92bf5-0e5d-4372-a801-1d4e2895be65", "4ffaecc0-3047-4da7-abe2-dd4163f17e61"]}
```

## Outputs: The service returns json with the fields:
- maxCleanTime: the maximum time to clean a property in the list
- minCleanTime: the minimum time to clean a property in the list
- totalCleanTime: the total time taken to clean all properties in the list
- idsCounted: total number of properties in the list for which data was gathered
- entriesWithNoCleanTime: number of properties where no clean time data was given
- entriesWithNoIds: number of properties where no id data was given(if this is non-zero something probably went very wrong with the data that was passed)

## Use test.py to test:
```
python test.py
```

## You can also use curl:
```
curl -X POST http://127.0.0.1:5000/ -H 'Content-Type: application/json' -d '{"ids":["e3e70682-c209-4cac-629f-6fbed82c07cd", "16a92bf5-0e5d-4372-a801-1d4e2895be65", "4ffaecc0-3047-4da7-abe2-dd4163f17e61"]}'
```

## Sample response:
```
{"entriesWithNoCleanTime":0,"entriesWithNoIds":0,"idsCounted":3,"maxCleanTime":2.91691406956171,"minCleanTime":2.29352616732206,"totalCleanTime":7.72456219718605}
```

## Other notes:
### We hit the endpoint like this:
```
https://housekeeping.vacasa.io/cleans?filter[id][in]=16a92bf5-0e5d-4372-a801-1d4e2895be65,e3e70682-c209-4cac-629f-6fbed82c07cd
```

### Seems like we ought to use something like:
```
https://housekeeping.vacasa.io/cleans?fields[clean]="predicted_clean_time"
```
### to minimize the amount of data we need to receive
but this returns the same as the filter endpoint above.
### the filter verb makes more sense to me so ill go with that
