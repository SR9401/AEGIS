from flask_restx import Namespace, Resource, fields
from db import Base, engine

Base.metadata.create_all(bind=engine)
api = Namespace('users', description='User operations')

user_model = api.model('User', {
    'first_name': fields.String(required=True, description='First name of the user'),
    'last_name': fields.String(required=True, description='Last name of the user'),
    'email': fields.String(required=True, description='Email of the user')
})

api.route('auth/login')


api.route('missions')