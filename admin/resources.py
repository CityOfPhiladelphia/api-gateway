from marshmallow_sqlalchemy import ModelSchema, field_for

from models import db, Ban, Key
from restful import BaseResource, BaseListResource, QueryEngineMixin

class BanSchema(ModelSchema):
    id = field_for(Ban, 'id', dump_only=True)
    created_at = field_for(Ban, 'created_at', dump_only=True)
    updated_at = field_for(Ban, 'updated_at', dump_only=True)
    class Meta:
        model = Ban

ban_schema = BanSchema()
bans_schema = BanSchema(many=True)

class BanResource(BaseResource):
    schema = ban_schema
    model = Ban
    session = db.session

class BanListResource(QueryEngineMixin, BaseListResource):
    schema = bans_schema
    model = Ban
    session = db.session

class KeySchema(ModelSchema):
    id = field_for(Key, 'id', dump_only=True)
    created_at = field_for(Key, 'created_at', dump_only=True)
    updated_at = field_for(Key, 'updated_at', dump_only=True)
    class Meta:
        model = Key

key_schema = KeySchema()
keys_schema = KeySchema(many=True)

class KeyResource(BaseResource):
    schema = key_schema
    model = Key
    session = db.session

class KeyListResource(BaseListResource):
    schema = keys_schema
    model = Key
    session = db.session
