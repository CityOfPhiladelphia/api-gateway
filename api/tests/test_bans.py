import pytest

from shared_fixtures import app, model_fixtures
from restful_ben.test_utils import json_call, dict_contains, iso_regex, login

def test_create_ban(app, model_fixtures):
    test_client = app.test_client()
    csrf_token = login(test_client)

    response = json_call(test_client.post, '/bans', {
        'active': True,
        'title': 'awful scraper',
        'cidr_blocks': [{
            'cidr': '76.32.36.23/32'
        },{
            'cidr': '76.32.36.28/32'
        }]
    }, headers={'X-CSRF': csrf_token})
    assert response.status_code == 201
    assert dict_contains(response.json, {
        'id': 2,
        'title': 'awful scraper',
        'description': None,
        'updated_at': iso_regex,
        'created_at': iso_regex
    })
    assert len(response.json['cidr_blocks']) == 2
    assert dict_contains(response.json['cidr_blocks'][0], {
        'id': 2,
        'ban': 2,
        'cidr': '76.32.36.23/32',
        'updated_at': iso_regex,
        'created_at': iso_regex
    })
    assert dict_contains(response.json['cidr_blocks'][1], {
        'id': 3,
        'ban': 2,
        'cidr': '76.32.36.28/32',
        'updated_at': iso_regex,
        'created_at': iso_regex
    })

def test_get_ban(app, model_fixtures):
    test_client = app.test_client()
    login(test_client)

    response = json_call(test_client.get, '/bans/1')
    assert response.status_code == 200
    assert dict_contains(response.json, {
        'id': 1,
        'title': 'foo',
        'description': None,
        'updated_at': iso_regex,
        'created_at': iso_regex
    })
    assert len(response.json['cidr_blocks']) == 1
    assert dict_contains(response.json['cidr_blocks'][0], {
        'id': 1,
        'ban': 1,
        'cidr': '10.0.0.0/16',
        'updated_at': iso_regex,
        'created_at': iso_regex
    })

def test_list_bans(app, model_fixtures):
    test_client = app.test_client()
    login(test_client)

    response = json_call(test_client.get, '/bans')
    assert response.status_code == 200
    assert response.json['count'] == 1
    assert response.json['page'] == 1
    assert response.json['total_pages'] == 1
    assert len(response.json['data']) == 1
    assert dict_contains(response.json['data'][0], {
        'id': 1,
        'title': 'foo',
        'description': None,
        'updated_at': iso_regex,
        'created_at': iso_regex
    })
    assert len(response.json['data'][0]['cidr_blocks']) == 1
    assert dict_contains(response.json['data'][0]['cidr_blocks'][0], {
        'id': 1,
        'ban': 1,
        'cidr': '10.0.0.0/16',
        'updated_at': iso_regex,
        'created_at': iso_regex
    })

def test_query_by_ip(app, model_fixtures):
    test_client = app.test_client()

    url = '/bans/cidr-blocks?cidr__contains=10.0.23.45'

    response = json_call(test_client.get, url, headers={'Authorization': 'Bearer testtoken'})
    assert response.status_code == 200
    assert response.json['count'] == 1
    assert response.json['page'] == 1
    assert response.json['total_pages'] == 1
    assert len(response.json['data']) == 1
    assert dict_contains(response.json['data'][0], {
        'id': 1,
        'ban': 1,
        'cidr': '10.0.0.0/16',
        'updated_at': iso_regex,
        'created_at': iso_regex
    })
