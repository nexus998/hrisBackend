from bson import ObjectId
from bson.json_util import dumps
from flask import request, Response
from flask_restful import Resource
import pandas as pd
import json

from database import cluster
from user_management import validate_group

field_template = {
    'name': '',
    'type': ''
}

entity_template = {
    'parent_entity_id': '',
    'name': '',
    'fields': [field_template]
}


class Entity(Resource):
    def get(self, group):
        gr = cluster[group]
        entities = gr['entity']
        validate_group(group, request.headers['authorization'])
        return Response(dumps({'group_name': group, 'data': entities.find({})}), mimetype='application/json')

    def post(self, group):
        gr = cluster[group]
        entities = gr['entity']
        validate_group(group, request.headers['authorization'])
        body = request.get_json()
        inserted = entities.insert_one(body)
        return {'_id': str(inserted.inserted_id)}, 200


class EntityModify(Resource):
    def put(self, group, entity_id):
        gr = cluster[group]
        entities = gr['entity']
        validate_group(group, request.headers['authorization'])

        current_fields = entities.find_one({'_id': ObjectId(entity_id)})['fields']

        data = {'$set': request.get_json()}
        entities.update({'_id': ObjectId(entity_id)}, data)

        j = request.get_json()

        da = gr['entity_data']
        # for x in range(len(j['fields'])):
        new_name = j['fields'][0]['name']
        # print(x, new_name, current_fields[x]['name'])
        old_name = current_fields[0]['name']
        d = da.find({'entity_id': entity_id})
        counter = 0
        for unit in d:

            print(counter)
            old_data = unit['data'][old_name]
            print(unit['data'])
            print(da.find_one({'_id': unit['_id']})['data'])
            print(new_name, old_data, old_name, old_data)
            da.update_one({'_id': unit['_id']}, {'$set': {'data.' + new_name: old_data}, '$unset': {'data.' + old_name: ""}})
            counter += 1
            # da.update_one({'_id': unit['_id']}, {'$set': {'data.' + new_name: old_data}})

        # da.update({'entity_id': entity_id}, {'$set': {'data.' + current_fields[x]['name']: j['fields'][x]['name']}})

        return Response(dumps(entities.find_one({'_id': ObjectId(entity_id)})), mimetype='application/json')

    def delete(self, group, entity_id):
        gr = cluster[group]
        entities = gr['entity']
        validate_group(group, request.headers['authorization'])
        entities.delete_one({'_id': ObjectId(entity_id)})
        return 'OK', 200


class Field(Resource):
    def get(self, group, entity_id):
        gr = cluster[group]
        entities = gr['entity']
        validate_group(group, request.headers['authorization'])
        return Response(dumps(entities.find_one({'_id': ObjectId(entity_id)})['fields']), mimetype='application/json')
    def post(self, group, entity_id):
        gr = cluster[group]
        entities = gr['entity']
        validate_group(group, request.headers['authorization'])
        data = {'$push': {'fields': request.get_json()}}
        entities.update_one({'_id': ObjectId(entity_id)}, data)
        return Response(dumps(entities.find_one({'_id': ObjectId(entity_id)})['fields']), mimetype='application/json')
    def delete(self, group, entity_id):
        gr = cluster[group]
        entities = gr['entity']
        validate_group(group, request.headers['authorization'])
        data = {'$pull': {'fields': {'name': request.get_json()['name']}}}
        entities.update_one({'_id': ObjectId(entity_id)}, data)
        return 'OK', 200


class EntityData(Resource):
    def get(self, group, entity_id):
        gr = cluster[group]
        entities_data = gr['entity_data']
        validate_group(group, request.headers['authorization'])
        response = dumps(entities_data.find({'entity_id': entity_id}))
        return Response(response, mimetype='application/json')

    def post(self, group, entity_id):
        gr = cluster[group]
        entities_data = gr['entity_data']
        validate_group(group, request.headers['authorization'])
        data = {
            'entity_id': entity_id,
            'data': request.get_json()
        }
        inserted = entities_data.insert_one(data)

        return {'_id': str(inserted.inserted_id)}, 200

    def delete(self, group, entity_id):
        gr = cluster[group]
        entities_data = gr['entity_data']
        validate_group(group, request.headers['authorization'])
        data = request.get_json()
        entities_data.delete_one({'entity_id': entity_id, '_id': ObjectId(data['_id'])})
        return "OK", 200


class EntityDataFile(Resource):
    def get(self, group, entity_id):
        gr = cluster[group]
        entities_data = gr['entity_data']
        # validate_group(group, request.headers['authorization'])
        response = json.loads(dumps(entities_data.find({'entity_id': entity_id})))

        data_list = []
        for x in range(len(response)):
            data_list.append(response[x]['data'])

        df = pd.read_json(dumps(data_list))
        csv = df.to_csv()

        return Response(
            csv,
            mimetype="text/csv",
            headers={"Content-disposition": "attachment; filename=report.csv"})

