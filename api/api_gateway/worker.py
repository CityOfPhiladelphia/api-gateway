import os
import time
import json
import logging
from functools import reduce
from itertools import groupby
from datetime import datetime

import boto3
import arrow
from sqlalchemy import create_engine

FORMAT = '[%(asctime)-15s] %(levelname)s [%(name)s] %(message)s'
logging.basicConfig(format=FORMAT, level=logging.INFO)
logger = logging.getLogger('analytics_worker')

sqs = boto3.client('sqs')

upsert_sql = '''
INSERT INTO requests_aggregates (key_id,
                                 ip,
                                 endpoint_name,
                                 minute,
                                 request_count,
                                 sum_elapsed_time,
                                 sum_bytes,
                                 sum_2xx,
                                 sum_3xx,
                                 sum_4xx,
                                 sum_429,
                                 sum_5xx)
VALUES
(%(key_id)s,
 %(ip)s,
 %(endpoint_name)s,
 %(minute)s,
 %(request_count)s,
 %(sum_elapsed_time)s,
 %(sum_bytes)s,
 %(sum_2xx)s,
 %(sum_3xx)s,
 %(sum_4xx)s,
 %(sum_429)s,
 %(sum_5xx)s)
ON CONFLICT ((COALESCE(key_id, -1)), ip, (COALESCE(endpoint_name, '&&--')), minute)
DO UPDATE
SET request_count = requests_aggregates.request_count + %(request_count)s,
    sum_elapsed_time = requests_aggregates.sum_elapsed_time + %(sum_elapsed_time)s,
    sum_bytes = requests_aggregates.sum_bytes + %(sum_bytes)s,
    sum_2xx = requests_aggregates.sum_2xx + %(sum_2xx)s,
    sum_3xx = requests_aggregates.sum_3xx + %(sum_3xx)s,
    sum_4xx = requests_aggregates.sum_4xx + %(sum_4xx)s,
    sum_429 = requests_aggregates.sum_429 + %(sum_429)s,
    sum_5xx = requests_aggregates.sum_5xx + %(sum_5xx)s;
'''

def get_aggrate_group_key(request):
    return (request['token_id'], request['user_ip'], request['endpoint_name'],)

def get_request_minute(request):
    return arrow.get(request['start_time']).floor('minute').datetime

def aggregate_requests(messages):
    requests = map(lambda x: json.loads(x['Body']), messages)
    for key, groups in groupby(requests, get_aggrate_group_key):
        for minute, grouped_by_minute in groupby(groups, get_request_minute):
            aggregate = {
                'key_id': key[0],
                'ip': key[1],
                'endpoint_name': key[2],
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
                aggregate['sum_bytes'] += request['content_length'] or 0

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

def get_messages(sqs_queue_url, total_count=0, max_total=100, wait_time_seconds=20, max_messages_per_call=10):
    response = sqs.receive_message(
        QueueUrl=sqs_queue_url,
        MaxNumberOfMessages=max_messages_per_call,
        WaitTimeSeconds=wait_time_seconds
    )

    if 'Messages' not in response:
        return []

    num_messages = len(response['Messages'])
    total_count += num_messages

    if num_messages == max_messages_per_call and total_count < max_total:
        return response['Messages'] + get_messages(total_count=total_count,
                                                   max_total=max_total,
                                                   wait_time_seconds=0,
                                                   max_messages_per_call=max_messages_per_call)

    return response['Messages']

def batch(iterable, n=1):
    l = len(iterable)
    for ndx in range(0, l, n):
        yield iterable[ndx:min(ndx + n, l)]

def get_delete_handle(message):
    return {
        'Id': message['MessageId'],
        'ReceiptHandle': message['ReceiptHandle']
    }

def delete_messages(sqs_queue_url, messages):
    for message_batch in batch(messages, 10):
        sqs.delete_message_batch(
            QueueUrl=sqs_queue_url,
            Entries=list(map(get_delete_handle, message_batch)))

## TODO: set consumption rate
## TODO: handle sigterm?
def run_worker(sql_alchemy_connection=None, sqs_queue_url=None, num_runs=1, sleep=0):
    connection_string = sql_alchemy_connection or os.getenv('SQLALCHEMY_DATABASE_URI')
    sqs_queue_url = sqs_queue_url or os.getenv('SQS_QUEUE_URL')

    engine = create_engine(connection_string) ## creates connection pool

    logger.info('Analytics worker up...')

    for n in range(0, num_runs):
        if n > 0 and sleep > 0:
            time.sleep(sleep)

        messages = get_messages(sqs_queue_url)

        if len(messages) == 0:
            continue

        conn = engine.raw_connection()

        with conn.cursor() as cur:
            for aggregate in aggregate_requests(messages):
                cur.execute(upsert_sql, aggregate)

        conn.close() ## returns connection to pool

        delete_messages(sqs_queue_url, messages)
