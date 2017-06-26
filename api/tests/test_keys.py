import re
from datetime import datetime

import pytest

from shared_fixtures import app, model_fixtures
from restful_ben.test_utils import json_call, dict_contains, iso_regex, login

key_regex = re.compile('^[0-9a-f]{64}$')

def test_create_key(app, model_fixtures):
    test_client = app.test_client()
    csrf_token = login(test_client)

    response = json_call(test_client.post, '/keys', {
        'active': True,
        'owner_name': 'john doe'
    }, headers={'X-CSRF': csrf_token})
    assert response.status_code == 201
    assert dict_contains(response.json, {
        'id': 2,
        'active': True,
        'owner_name': 'john doe',
        'contact_email': None,
        'contact_name': None,
        'key': key_regex,
        'updated_at': iso_regex,
        'created_at': iso_regex
    })

def test_get_key(app, model_fixtures):
    test_client = app.test_client()
    login(test_client)

    response = json_call(test_client.get, '/keys/1')
    assert response.status_code == 200
    assert dict_contains(response.json, {
        'id': 1,
        'active': True,
        'owner_name': 'jane doe',
        'contact_email': None,
        'contact_name': None,
        'updated_at': iso_regex,
        'created_at': iso_regex
    })
    assert 'key' not in response.json

def test_list_keys(app, model_fixtures):
    test_client = app.test_client()
    login(test_client)

    response = json_call(test_client.get, '/keys')
    assert response.status_code == 200
    assert response.json['count'] == 1
    assert response.json['page'] == 1
    assert response.json['total_pages'] == 1
    assert len(response.json['data']) == 1
    for key in response.json['data']:
        assert 'key' not in key
    assert dict_contains(response.json['data'][0], {
        'id': 1,
        'active': True,
        'owner_name': 'jane doe',
        'contact_email': None,
        'contact_name': None,
        'updated_at': iso_regex,
        'created_at': iso_regex
    })

def test_query_for_key(app, model_fixtures):
    test_client = app.test_client()
    csrf_token = login(test_client)

    response = json_call(test_client.post, '/keys', {
        'active': True,
        'owner_name': 'john doe'
    }, headers={'X-CSRF': csrf_token})
    assert response.status_code == 201
    key = response.json

    test_client = app.test_client()

    url = '/keys?key={}&active=true'.format(
        key['key'],
        datetime.utcnow().isoformat())

    response = json_call(test_client.get, url, headers={'Authorization': 'Bearer testtoken'})
    assert response.status_code == 200
    assert response.json['count'] == 1
    assert response.json['page'] == 1
    assert response.json['total_pages'] == 1
    assert len(response.json['data']) == 1
    assert dict_contains(response.json['data'][0], {
        'id': key['id'],
        'active': True,
        'owner_name': 'john doe',
        'contact_email': None,
        'contact_name': None,
        'updated_at': iso_regex,
        'created_at': iso_regex
    })
    assert 'key' not in response.json['data'][0]

def test_update_key(app, model_fixtures):
    test_client = app.test_client()
    csrf_token = login(test_client)

    response = json_call(test_client.get, '/keys/1')
    assert response.status_code == 200
    key = response.json

    key['contact_email'] = 'foo@foo.com'

    response = json_call(test_client.put, '/keys/1', key, headers={'X-CSRF': csrf_token})
    assert response.status_code == 200
    assert dict_contains(response.json, {
        'id': 1,
        'active': True,
        'owner_name': 'jane doe',
        'contact_email': 'foo@foo.com',
        'contact_name': None,
        'updated_at': iso_regex,
        'created_at': iso_regex
    })
    assert 'key' not in response.json
    assert key['updated_at'] < response.json['updated_at']

def test_delete_key(app, model_fixtures):
    test_client = app.test_client()
    csrf_token = login(test_client)

    response = json_call(test_client.get, '/keys/1')
    assert response.status_code == 200

    response = test_client.delete('/keys/1', headers={'X-CSRF': csrf_token})
    assert response.status_code == 204

    response = json_call(test_client.get, '/keys/1')
    assert response.status_code == 404
