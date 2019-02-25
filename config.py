from flask_sqlalchemy import SQLAlchemy
from flask import Flask, render_template, redirect, request, session, make_response

# init app and configure server
app = Flask(__name__)
app.config['SECRET_KEY'] = '1515dd15dd3d5d1a51b5af515ca'

# add data base
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

admin = {'login':'admin',
         'password':'nimda'}