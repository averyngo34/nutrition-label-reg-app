import datetime
import argparse
import logging
import json
import os
import requests
from datetime import date
import azure.functions as func
import lib.cosmos as cosmos


LOCAL_SERVER = "http://127.0.0.1:5000"
AZURE_SERVER = "https://sicc-ajm-project4.azurewebsites.net"
API_ENDPOINT = "summary"
CONTAINER = cosmos.init(cosmos.ENDPOINT, cosmos.KEY, cosmos.DATABASE,
                        cosmos.DATABASE, cosmos.PARTITION_KEY)


def main(mytimer: func.TimerRequest) -> None:
    utc_timestamp = datetime.datetime.utcnow().replace(
        tzinfo=datetime.timezone.utc).isoformat()

    if mytimer.past_due:
        print('The timer is past due!')

    print('Python timer trigger function ran at %s', utc_timestamp)
    send_to_web_app()


def send_to_web_app():
    data = cosmos.query(
        CONTAINER, cosmos.TODAY_QUERY.format(str(date.today())))
    print(f"Received query response: {data}")
    payload = {'request':  json.dumps(data) }
    print(f"Received query data of type {type(data)}: {data}")
    #data = {'username': 'Olivia', 'password': '123'}
    endpoint = os.path.join(AZURE_SERVER, API_ENDPOINT)
    print(f"Sending to endpoint {endpoint}")
    r = requests.post(endpoint, data=payload)
    print(r.text)