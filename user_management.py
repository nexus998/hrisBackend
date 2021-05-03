import bcrypt
import bson
import pymongo
from bson import ObjectId
from bson.json_util import dumps
from flask import request, abort, Response
from flask_restful import Resource

from database import cluster


def get_authorized_user(authorization_code):
    db = cluster['maindb']
    auth = db['authentication']
    user_id = auth.find_one({'_id': ObjectId(authorization_code)})['user_id']
    users = db['user']
    return users.find_one({'_id': user_id})


def validate_group(group, authorization_code):
    try:
        user_groups = get_authorized_user(authorization_code)['groups']
        if group not in user_groups:
            abort(400, 'User cannot access this group/group does not exist.')
    except bson.errors.InvalidId:
        abort(400, 'Invalid authorization ID.')


class Login(Resource):
    @staticmethod
    def post():
        db = cluster['maindb']
        user = db['user']
        body = request.get_json()
        print(body)
        existing_user = user.find_one({'username': body['username']})
        if existing_user is not None:
            check_psw = bcrypt.checkpw(body['password'].encode('utf-8'), existing_user['password'])
            if not check_psw:
                abort(400, 'Wrong password.')

            # get authentication code or create one
            auth = db['authentication']
            data = {'$set': {'user_id': existing_user['_id']}}
            code = auth.update({'user_id': existing_user['_id']}, data, upsert=True)
            return Response(dumps({'code': str(auth.find_one({'user_id': existing_user['_id']})['_id'])}), 200)

        abort(400, 'Wrong username.')


class Register(Resource):
    @staticmethod
    def post():
        db = cluster['maindb']
        user = db['user']
        body = request.get_json()

        body['password'] = bcrypt.hashpw(body['password'].encode('utf-8'), bcrypt.gensalt())
        try:
            inserted = user.insert_one(body)
            return {'_id:': str(inserted.inserted_id)}, 200
        except pymongo.errors.DuplicateKeyError:
            abort(400, 'Username already exists. Please use a different username.')
