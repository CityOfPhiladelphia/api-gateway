from flask import request
from flask_restful import Resource, abort
from marshmallow_sqlalchemy import ModelSchema, field_for

from models import db, Ban, Key

class BaseResource(Resource):
    def get(self, instance_id):
        instance = self.session.query(self.model).filter_by(id=instance_id).first() ## TODO: get pk from model
        if not instance:
            abort(404, message="{} {} not found".format(self.model_name, instance_id))
        return self.schema.dump(instance).data

    def put(self, instance_id):
        raw_body = request.json

        instance = self.session.query(self.model).filter_by(id=instance_id).first() ## TODO: get pk from model
        if not instance:
            abort(404, message="{} {} not found".format(self.model_name, instance_id))

        instance_load = self.schema.load(raw_body, session=self.session, instance=instance)

        if instance_load.errors:
            abort(400, errors=instance_load.errors)

        self.session.commit()
        self.session.refresh(instance)
        return self.schema.dump(instance).data

class BaseListResource(Resource):
    def post(self):
        raw_body = request.json
        instance_load = self.schema.load(raw_body, session=self.session)

        if instance_load.errors:
            abort(400, errors=instance_load.errors)

        instance = instance_load.data

        self.session.add(instance)
        self.session.commit()
        self.session.refresh(instance)
        return self.schema.dump(instance).data

    def get(self):
        instances = self.session.query(self.model)
        return self.schema.dump(instances).data

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
    model_name = 'Ban'
    session = db.session

class BanListResource(BaseListResource):
    schema = bans_schema
    model = Ban
    model_name = 'Ban'
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
    model_name = 'Key'
    session = db.session

class KeyListResource(BaseListResource):
    schema = keys_schema
    model = Key
    model_name = 'Key'
    session = db.session
