from marshmallow_sqlalchemy import ModelSchema, field_for
from marshmallow import fields
from sqlalchemy.dialects.postgresql import CIDR

from models import db, Ban, Key
from restful import BaseResource, BaseListResource, QueryEngineMixin

class BanSchema(ModelSchema):
    class Meta:
        model = Ban

    id = field_for(Ban, 'id', dump_only=True)
    cidr = fields.Str()
    created_at = field_for(Ban, 'created_at', dump_only=True)
    updated_at = field_for(Ban, 'updated_at', dump_only=True)

ban_schema = BanSchema()
bans_schema = BanSchema(many=True)

class BanResource(BaseResource):
    single_schema = ban_schema
    model = Ban
    session = db.session

class BanListResource(QueryEngineMixin, BaseListResource):
    single_schema = ban_schema
    many_schema = bans_schema
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
    single_schema = key_schema
    model = Key
    session = db.session

class KeyListResource(BaseListResource):
    single_schema = key_schema
    many_schema = keys_schema
    model = Key
    session = db.session
