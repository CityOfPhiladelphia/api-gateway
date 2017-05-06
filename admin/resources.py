from flask import request
from flask_restful import Resource, abort
from marshmallow_sqlalchemy import ModelSchema, field_for

from models import db, Ban, Key

class BanSchema(ModelSchema):
    id = field_for(Ban, 'id', dump_only=True)
    created_at = field_for(Ban, 'created_at', dump_only=True)
    updated_at = field_for(Ban, 'updated_at', dump_only=True)
    class Meta:
        model = Ban

ban_schema = BanSchema()
bans_schema = BanSchema(many=True)

class BanResource(Resource):
    def get(self, ban_id):
        ban = db.session.query(Ban).filter_by(id=ban_id).first()
        if not ban:
            abort(404, message="Ban {} not found".format(ban_id))
        return ban_schema.dump(ban).data

    def put(self, ban_id):
        raw_body = request.json

        ban = db.session.query(Ban).filter_by(id=ban_id).first()
        if not ban:
            abort(404, message="Ban {} not found".format(ban_id))

        ban_load = ban_schema.load(raw_body, session=db.session, instance=ban)

        if ban_load.errors:
            abort(400, errors=ban_load.errors)

        db.session.commit()
        db.session.refresh(ban)
        return ban_schema.dump(ban).data

class BanListResource(Resource):
    def post(self):
        raw_body = request.json
        ban_load = ban_schema.load(raw_body, session=db.session)

        if ban_load.errors:
            abort(400, errors=ban_load.errors)

        ban = ban_load.data

        db.session.add(ban)
        db.session.commit()
        db.session.refresh(ban)
        return ban_schema.dump(ban).data

    def get(self):
        bans = db.session.query(Ban)
        return bans_schema.dump(bans).data
