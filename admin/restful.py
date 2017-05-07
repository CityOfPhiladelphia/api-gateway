from flask import request
from flask_restful import Resource, abort

### TODO: separate this out into library

class BaseResource(Resource):
    def get(self, instance_id):
        instance = self.session.query(self.model).filter_by(id=instance_id).first() ## TODO: get pk from model
        if not instance:
            abort(404, errors=['{} {} not found'.format(self.model.__name__, instance_id)])
        return self.schema.dump(instance).data

    def put(self, instance_id):
        raw_body = request.json

        instance = self.session.query(self.model).filter_by(id=instance_id).first() ## TODO: get pk from model
        if not instance:
            abort(404, errors=['{} {} not found'.format(self.model.__name__, instance_id)])

        instance_load = self.schema.load(raw_body, session=self.session, instance=instance)

        if instance_load.errors:
            abort(400, errors=instance_load.errors)

        self.session.commit()
        self.session.refresh(instance)
        return self.schema.dump(instance).data

class QueryEngineMixin(object):
    page_key = '$page'
    page_size_key = '$page_size'
    default_page_size = 100

    field_selection_key = '$fields'
    order_by_key = '$order_by'

    allowed_operations = [
        'eq', # =
        'ne', # !=
        'lt', # <
        'le', # <=
        'gt', # >
        'ge', # >=
        'contains',
        'like',
        'ilike',
        'in_', # in
        'notin_', # not in
        'notlike', # not like
        'notilike', # not ilike
        'is',
        'isnot', # is not
        'startswith',
        'endswith',
        'is_distinct_from', # a IS DISTINCT FROM b
        'isnot_distinct_from', # a IS NOT DISTINCT FROM b
    ]

    alias_operations = {
        'lte': 'le',
        'gte': 'ge',
        'in': 'in_',
        'notin': 'notin_'
    }

    @property
    def reserved_keys(self):
        return [
            self.page_key,
            self.page_size_key,
            self.field_selection_key,
            self.order_by_key
        ]

    def get_filters(self):
        filters = []
        for key, value in request.args.items():
            if key in self.reserved_keys:
                continue
            split_key = key.split('__')
            field_key = split_key[0]
            num_args = len(split_key)
            if num_args == 1:
                op = 'eq'
            elif num_args == 2:
                op = split_key[1]
            else:
                abort(400, errors=['Invalid filter argument `{}`'.format(key)])
            field = getattr(self.model, field_key, None)
            if field is None:
                abort(400, errors=['Field `{}` does not exist on {}'.format(field_key, self.model.__name__)])
            if op in self.alias_operations:
                op = self.alias_operations[op]
            if op not in self.allowed_operations:
                abort(400, errors=['Operator `{}` not available on {}'.format(op, self.model.__name__)])
            field_op = list(filter(
                lambda e: hasattr(field, e % op),
                ['%s', '%s_', '__%s__']
            ))[0] % op
            filters.append(getattr(field, field_op)(value))
        return filters

    def get_pagination(self):
        raw_page = request.args.get(self.page_key)
        raw_page_size = request.args.get(self.page_size_key)
        
        if raw_page is None:
            page = 1
        else:
            try:
                page = int(raw_page)
                assert(page > 0)
            except:
                abort(400, errors=['`{}` is not a postive integer'.format(self.page_key)])

        if raw_page_size is None:
            page_size = self.default_page_size
        else:
            try:
                page_size = int(raw_page_size)
                assert(page_size >= 0)
            except:
                abort(400, errors=['`{}` must be an integer greater than or equal to 0'.format(self.page_size_key)])

        offset = (page - 1) * page_size

        return offset, page_size

    def get_ordering(self):
        raw_ordering = request.args.get(self.order_by_key)
        ordering = []

        if raw_ordering is not None:
            for raw_order_field in raw_ordering.split(','):
                if raw_order_field[0:1] == '-':
                    order = 'desc'
                    field = raw_order_field[1:]
                else:
                    order = 'asc'
                    field = raw_order_field

                if not hasattr(self.model, field):
                    abort(400, errors=['`{}` does not exist on {}'.format(field, self.model.__name__)])

                model_field = getattr(self.model, field)
                if order == 'desc':
                    ordering.append(model_field.desc())
                else:
                    ordering.append(model_field)
        else:
            ordering.append(self.model.id) ## TODO: do not assume id is the pk

        return ordering

    def get_field_selection(self):
        raw_fields = request.args.get(self.field_selection_key)

        if raw_fields is None:
            return [self.model]

        fields = []
        for raw_field in raw_fields.split(','):
            if not hasattr(self.model, raw_field):
                abort(400, errors=['`{}` does not exist on {}'.format(raw_field, self.model.__name__)])
            fields.append(getattr(self.model, raw_field))
        return fields

    def generate_query(self):
        fields = self.get_field_selection()
        filters = self.get_filters()
        offset, limit = self.get_pagination()
        ordering = self.get_ordering()

        return self.session.query(*fields)\
        .filter(*filters)\
        .order_by(*ordering)\
        .offset(offset)\
        .limit(limit)

    def get(self):
        instances = self.generate_query()
        out = self.schema.dump(instances).data
        print(out)
        return out

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
