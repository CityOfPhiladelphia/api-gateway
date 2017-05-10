from marshmallow_sqlalchemy import ModelSchema, field_for
from marshmallow import fields
from sqlalchemy.dialects.postgresql import CIDR

from models import db, Ban, CIDRBlock, Key
from restful import RetrieveUpdateDeleteResource, CreateListResource, QueryEngineMixin, BaseResource

## CIDR Blocks

class CIDRBlockSchema(ModelSchema):
    class Meta:
        model = CIDRBlock
        sqla_session = db.session

    id = field_for(Ban, 'id', dump_only=True)
    cidr = fields.Str()
    created_at = field_for(Ban, 'created_at', dump_only=True)
    updated_at = field_for(Ban, 'updated_at', dump_only=True)

cidr_block_schema = CIDRBlockSchema()
cidr_blocks_schema = CIDRBlockSchema(many=True)

class CIDRBlockResource(RetrieveUpdateDeleteResource):
    methods = ['GET','DELETE']
    single_schema = cidr_block_schema
    model = CIDRBlock
    session = db.session

class CIDRBlockListResource(QueryEngineMixin, BaseResource):
    many_schema = cidr_blocks_schema
    model = CIDRBlock
    session = db.session
    operator_overrides = {
        'cidr': {
            'contains': CIDRBlock.cidr.op('>>=')
        }
    }

## Bans

class BanSchema(ModelSchema):
    class Meta:
        model = Ban

    id = field_for(Ban, 'id', dump_only=True)
    title = field_for(Ban, 'title', required=True)
    description = field_for(Ban, 'description', required=True)
    cidr_blocks = fields.Nested(CIDRBlockSchema, many=True, required=True)
    created_at = field_for(Ban, 'created_at', dump_only=True)
    updated_at = field_for(Ban, 'updated_at', dump_only=True)

class BanSchemaPUTGET(BanSchema):
    cidr_blocks = fields.Nested(CIDRBlockSchema, dump_only=True, many=True)

ban_schema = BanSchema()
ban_schema_put_get= BanSchemaPUTGET()
bans_schema = BanSchema(many=True)

class BanResource(RetrieveUpdateDeleteResource):
    single_schema = ban_schema_put_get
    model = Ban
    session = db.session

class BanListResource(QueryEngineMixin, CreateListResource):
    single_schema = ban_schema
    many_schema = bans_schema
    model = Ban
    session = db.session

## Keys

class KeySchema(ModelSchema):
    class Meta:
        model = Key

    id = field_for(Key, 'id', dump_only=True)
    created_at = field_for(Key, 'created_at', dump_only=True)
    updated_at = field_for(Key, 'updated_at', dump_only=True)

key_schema = KeySchema()
keys_schema = KeySchema(many=True)

class KeyResource(RetrieveUpdateDeleteResource):
    single_schema = key_schema
    model = Key
    session = db.session

class KeyListResource(CreateListResource):
    single_schema = key_schema
    many_schema = keys_schema
    model = Key
    session = db.session
