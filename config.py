from flask_sqlalchemy import SQLAlchemy
from flask import *
from flask_restful import reqparse, abort, Api, Resource
from random import seed, choice

# init app and configure server
app = Flask(__name__)
app.config['SECRET_KEY'] = '1515dd15dd3d5d1a51b5af515ca'

seed()

# init API
api = Api(app)
parser = reqparse.RequestParser()
parser.add_argument('theme_name', required=True)
parser.add_argument('content', required=True)
parser.add_argument('user_id', required=True, type=int)


# add data base
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

admin = {'login':'admin',
         'password':'nimda'}