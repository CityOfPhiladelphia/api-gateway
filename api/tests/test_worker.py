import json
import uuid
import os
from datetime import datetime

import pytest
import boto3
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from api_gateway.worker import run_worker
from api_gateway.models import RequestsAggregate, Key
import api_gateway

from shared_fixtures import models
from restful_ben.test_utils import dict_contains, iso_regex

class MockSQS(object):
    def __init__(self):
        self.queue = []

    def _add(self, message):
        self.queue.append({
            'Body': json.dumps(message),
            'MessageId': str(uuid.uuid4()),
            'ReceiptHandle': str(uuid.uuid4())
        })

    def add(self, messages):
        if isinstance(messages, list):
            for message in messages:
                self._add(message)
        else:
            self._add(messages)

    def receive_message(self, *args, **kwargs):
        return {
            'Messages': self.queue
        }

    def delete_message_batch(self, *args, Entries=[], **kwargs):
        for entry in Entries:
            for item in self.queue:
                if item['MessageId'] == entry['Id'] and \
                   item['ReceiptHandle'] == entry['ReceiptHandle']:
                   self.queue.remove(item)

test_messages = [
    {
        'user_ip': '69.47.137.22',
        'token_id': None,
        'start_time': '2017-07-07T16:09:03.971Z',
        'request_id': 'a995de56-9931-4068-9201-dea831300b26',
        'endpoint_name': 'carto',
        'method': 'GET',
        'status_code': 200,
        'path': '/carto/api/v1/sql',
        'proxied_path': '/api/v1/sql',
        'elapsed_time': 234,
        'content_length': 2356
    },
    {
        'user_ip': '69.47.137.22',
        'token_id': None,
        'start_time': '2017-07-07T16:09:05.232Z',
        'request_id': '1fbeb0b9-8371-4543-9534-42c2646cdd48',
        'endpoint_name': 'carto',
        'method': 'GET',
        'status_code': 200,
        'path': '/carto/api/v1/sql',
        'proxied_path': '/api/v1/sql',
        'elapsed_time': 122,
        'content_length': 1279
    },
    {
        'user_ip': '45.23.222.23',
        'token_id': 1,
        'start_time': '2017-07-07T16:09:03.971Z',
        'request_id': '3a575ae2-9c48-4c36-9647-d156efa6647b',
        'endpoint_name': 'carto',
        'method': 'GET',
        'status_code': 200,
        'path': '/carto/api/v1/sql',
        'proxied_path': '/api/v1/sql',
        'elapsed_time': 234,
        'content_length': 2356
    },
    {
        'user_ip': '45.23.222.23',
        'token_id': 1,
        'start_time': '2017-07-07T16:09:05.232Z',
        'request_id': '4d5bc981-b0ec-40d6-8202-68c153c05448',
        'endpoint_name': 'carto',
        'method': 'GET',
        'status_code': 200,
        'path': '/carto/api/v1/sql',
        'proxied_path': '/api/v1/sql',
        'elapsed_time': 122,
        'content_length': 1279
    },
    {
        'user_ip': '45.23.222.25',
        'token_id': 1,
        'start_time': '2017-07-07T16:09:06.242Z',
        'request_id': '9ee4d8e9-8a41-48db-8de2-c8987ed50f43',
        'endpoint_name': 'carto',
        'method': 'GET',
        'status_code': 200,
        'path': '/carto/api/v1/sql',
        'proxied_path': '/api/v1/sql',
        'elapsed_time': 122,
        'content_length': 1279
    },
    {
        'user_ip': '45.23.222.25',
        'token_id': 1,
        'start_time': '2017-07-07T16:09:06.242Z',
        'request_id': '9ee4d8e9-8a41-48db-8de2-c8987ed50f43',
        'endpoint_name': 'carto',
        'method': 'GET',
        'status_code': 404,
        'path': '/carto/api/v1/sql',
        'proxied_path': '/api/v1/sql',
        'elapsed_time': 34,
        'content_length': 322
    }
]

def get_session():
    connection_string = os.getenv('SQLALCHEMY_DATABASE_URI')
    engine = create_engine(connection_string)
    Session = sessionmaker(bind=engine)
    return Session()

def test_worker(models, monkeypatch):
    mock_sqs = MockSQS()
    monkeypatch.setattr(api_gateway.worker, 'sqs', mock_sqs)

    session = get_session()
    session.add(Key(active=True, owner_name='jane doe'))
    session.commit()

    mock_sqs.add(test_messages)

    run_worker()

    aggregates = session.query(RequestsAggregate).all()

    session.close()

    assert len(aggregates) == 3
    assert dict_contains(aggregates[0].__dict__, {
        'id': 1,
        'key_id': None,
        'ip': '69.47.137.22',
        'endpoint_name': 'carto',
        'minute': datetime(2017, 7, 7, 12, 9),
        'request_count': 2,
        'sum_elapsed_time': 356,
        'sum_bytes': 3635,
        'sum_2xx': 2,
        'sum_3xx': 0,
        'sum_4xx': 0,
        'sum_429': 0,
        'sum_5xx': 0
    })
    assert dict_contains(aggregates[1].__dict__, {
        'id': 2,
        'key_id': 1,
        'ip': '45.23.222.23',
        'endpoint_name': 'carto',
        'minute': datetime(2017, 7, 7, 12, 9),
        'request_count': 2,
        'sum_elapsed_time': 356,
        'sum_bytes': 3635,
        'sum_2xx': 2,
        'sum_3xx': 0,
        'sum_4xx': 0,
        'sum_429': 0,
        'sum_5xx': 0
    })
    assert dict_contains(aggregates[2].__dict__, {
        'id': 3,
        'key_id': 1,
        'ip': '45.23.222.25',
        'endpoint_name': 'carto',
        'minute': datetime(2017, 7, 7, 12, 9),
        'request_count': 2,
        'sum_elapsed_time': 156,
        'sum_bytes': 1601,
        'sum_2xx': 1,
        'sum_3xx': 0,
        'sum_4xx': 1,
        'sum_429': 0,
        'sum_5xx': 0
    })
