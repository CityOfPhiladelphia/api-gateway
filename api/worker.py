import os
import json
from functools import reduce
from itertools import groupby
from datetime import datetime

import boto3
import arrow

sqs_queue_url = os.getenv('SQS_QUEUE_URL')

sqs = boto3.resource('sqs')

def get_aggrate_group_key(request):
    return (request['token_id'], request['user_ip'], request['endpoint_name'],)

def get_request_minute(request):
    return arrow.get(request['start_time']).floor('minute').datetime

def aggregate_requests(messages):
    requests = map(lambda x: json.loads(x['Body']), messages)
    for key, groups in groupby(requests, get_aggrate_group_key):
        for minute, grouped_by_minute in groupby(grouped_by_user, get_request_minute)
            aggregate = {
                'key_id': key[0],
                'ip': key[1],
                'endpoint_name': key[2]
                'minute': minute,
                'request_count': 0,
                'sum_elapsed_time': 0,
                'sum_bytes': 0,
                'sum_2xx': 0,
                'sum_3xx': 0,
                'sum_4xx': 0,
                'sum_429': 0,
                'sum_5xx': 0
            }

            for request in grouped_by_minute:
                aggregate['request_count'] += 1
                aggregate['sum_elapsed_time'] += request['elapsed_time']
                aggregate['sum_bytes'] += request['content_length']

                status = request['status_code']
                if 200 <= status < 300:
                    aggregate['sum_2xx'] += 1
                elif 300 <= status < 400:
                    aggregate['sum_3xx'] += 1
                elif status == 429:
                    aggregate['sum_429'] += 1
                elif 400 <= status < 500:
                    aggregate['sum_4xx'] += 1
                elif 500 <= status < 600:
                    aggregate['sum_5xx'] += 1

            yield aggregate

def upsert_aggregates():

while True:
    response = sqs.receive_message(
        QueueUrl=sqs_queue_url,
        MaxNumberOfMessages=10,
        WaitTimeSeconds=20
    )

    if len(response['Messages']) == 0:
        continue
