# VIN API
## An implementation of KoffieLabs_backend-challenge
```https://github.com/KoffieLabs/backend-challenge```
### By Paul Ferguson

A caching API which provides vehicle details as found in the  vPIC API.

## Install
clone the git repo, and install dependencies with pip:
```commandline
pip -r requirements.txt
```

## For testing, use Behave.
```
$ behave 
Feature: VIN API # features/endpoints.feature:2
...
```

## For local deployment, use Uvicorn
```
$ uvicorn main:app
INFO:     Started server process [220986]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
...
```

## For API details, use the OpenAPI docs.
Start a local deployment, and visit:
`http://127.0.0.1:8000/docs`

## Notes and to do
 - While testing, I ran into the VPIC API going down for maintenance late at night.  It might be a good idea to mock the api in testing, or download the offline DB and refresh it periodically, especially if high availability is a goal.
 - Consider the size in RAM of the SQLite database and potential Parquet files when loading large numbers of VINs.  It may be worthwhile to write the database to file and implement streaming for export.
 - Could add schema data to the OpenAPI docs, and schema enforcement via Pydantic, map_api_to_db doesn't scale well if we get more models.