import json
import uuid

import pytest
import boto3

from api_gateway.worker import _main
import api_gateway

from shared_fixtures import models

class MockSQS(object):
    def __init__(self):
        self.queue = []

    def _add(self, message):
        self.queue.append({
            'Body': json.dumps(message),
            'MessageId': uuid.uuid4(),
            'ReceiptHandle': uuid.uuid4()
        })

    def add(self, messages):
        if isinstance(messages, list):
            for message in messages:
                self._add(message)
        else:
            self._add(messages)

    def receive_message(self, *args, **kwargs):
        print('receive_message')
        return {
            'Messages': self.queue
        }

    def delete_message_batch(self, *args, Entries=[], **kwargs):
        for entry in Entries:
            for item in self.queue:
                if item['MessageId'] == entry['MessageId'] and \
                   item['ReceiptHandle'] == entry['ReceiptHandle']:
                   self.queue.pop(item)

def test_worker(models, monkeypatch):
    mock_sqs = MockSQS()
    monkeypatch.setattr(api_gateway.worker, 'sqs', mock_sqs)

    _main(None, None, 1, 0)
