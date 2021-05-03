
from flask import Flask
from flask_cors import CORS
from flask_restful import Api

from entity_management import Entity, EntityModify, Field, EntityData, EntityDataFile
from group_management import Group
from user_management import Register, Login

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
api = Api(app)

api.add_resource(Register, '/register')
api.add_resource(Login, '/login')
api.add_resource(Group, '/group')
api.add_resource(Entity, '/group/<string:group>/entity')
api.add_resource(EntityModify, '/group/<string:group>/entity/<string:entity_id>')
api.add_resource(Field, '/group/<string:group>/entity/<string:entity_id>/field')
api.add_resource(EntityData, '/group/<string:group>/entity/<string:entity_id>/data')
api.add_resource(EntityDataFile, '/group/<string:group>/entity/<string:entity_id>/data/export')

if __name__ == "__main__":
    app.run(debug=True)
