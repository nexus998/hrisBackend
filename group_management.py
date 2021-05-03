import bson
from bson import ObjectId
from flask import request, jsonify, abort
from flask_restful import Resource

from database import cluster
from user_management import get_authorized_user


class Group(Resource):
    def get(self):
        auth_header = request.headers['authorization']
        try:
            groups = get_authorized_user(auth_header)['groups']
            return jsonify({'data': groups})
        except bson.errors.InvalidId:
            abort(400, 'Authentication failed, because authorization ID is incorrect.')

    def post(self):
        db = cluster['maindb']
        auth = db['authentication']
        auth_header = request.headers['authorization']
        try:
            user_id = auth.find_one({'_id': ObjectId(auth_header)})['user_id']
            users = db['user']
            print(request.data)
            body = request.get_json()['name']
            print(body)
            # create new database for this group
            body_adjusted = str(body).lower().strip().replace(' ', '_')
            new_group = cluster[body_adjusted]
            # entity_collection = new_group['entity']
            new_group.create_collection('entity_data')
            new_group.create_collection('entity')
            # entity_collection.insert_one(entity_template)

            data = {'$push': {'groups': body_adjusted}}
            users.update_one({'_id': user_id}, data, upsert=True)
            return jsonify({'data': users.find_one({'_id': user_id})['groups']})

        except bson.errors.InvalidId:
            abort(400, 'Authentication failed, because authorization ID is incorrect.')