from flask import Flask, flash, redirect, url_for, session, request, logging
from flask.globals import request
from flask.json import jsonify
from flask_restful import Api, Resource
import warnings
import json
from typing import DefaultDict
from flask_sqlalchemy import SQLAlchemy

from db_model import db
from db_model import Userdata, Formdata, Vaccinedata

username = 'root'           
password = 'adkasghdih1919' # self pass    
host = '127.0.0.1'          
port = '3306'               
database = 'hackathon'    # self db

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{username}:{password}@{host}:{port}/{database}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
# db.create_all()

# 1. Add new users
# user_list = []
# for i in range(5):
#     user = Userdata(ID=i, Name='user{}'.format(i), 
#                     password='pass{}'.format(i), 
#                     identity="engineer", 
#                     email="user{}@gmail.com".format(i))
#     user_list.append(user)
# db.session.add_all(user_list)
# db.session.commit()
# user = Userdata.query.all()
# for i in user:
#     print(i.Name)

# 2. Add new form data
# form = Formdata(form_id=0, user_id=0)
# db.session.add(form)
# db.session.commit()

# 3. Add new vaccine type list
vaccine_list = []
az = Vaccinedata(vaccine_id=0, date='2021-07-01', vaccine_type='AZ', vaccine_amount=1000)
md = Vaccinedata(vaccine_id=1, date='2021-07-01', vaccine_type='MD', vaccine_amount=1000)
bnt = Vaccinedata(vaccine_id=2, date='2021-07-01', vaccine_type='BNT', vaccine_amount=1000)

vaccine_list.append(az)
vaccine_list.append(md)
vaccine_list.append(bnt)
db.session.add_all(vaccine_list)
db.session.commit()

