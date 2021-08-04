'''
2021/07/31 test flask_sqlalchemy
usage : 
        from db_model import db
        from db_model import Userdata, Formdata, Vaccinedata

        db.create_all()
        user1 = Userdata(ID=111111, Name='hehe', password='happyclick', identity="it engineer", email="hehe@gmail.com")
        db.session.add_all([user1])
        db.session.commit()
        user = Userdata.query.all()
        for i in user:
            print(i.ID, i.Name)
'''

from typing import DefaultDict
from flask_sqlalchemy import SQLAlchemy
from flask import Flask

username = 'root'           
password = 'adkasghdih1919' # self pass    
host = '127.0.0.1'          
port = '3306'               
database = 'hackathon'    # self db

# app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{username}:{password}@{host}:{port}/{database}'
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy()

class Userdata(db.Model):
    __tablename__ = 'userdata'
    ID = db.Column(db.Integer, primary_key=True) 
    Name = db.Column(db.String(64)) 
    password = db.Column(db.String(64))
    identity = db.Column(db.String(64))
    email = db.Column(db.String(64), unique=True)
    vaccine_type = db.Column(db.String(64), default="Null")
    vaccination = db.Column(db.String(64), default="N")

    def __repr__(self):
        return "<Role %r>" % self.Name

class Formdata(db.Model):
    __tablename__ = 'formdata'
    form_id = db.Column(db.Integer, primary_key=True) 
    user_id = db.Column(db.Integer) 
    username = db.Column(db.String(64))
    vaccine_type = db.Column(db.String(64))
    vaccine_date = db.Column(db.Date)

    def __repr__(self):
        return "<Role %r>" % self.form_id

class Vaccinedata(db.Model):
    __tablename__ = 'vaccinedata' 
    vaccine_id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date) 
    vaccine_type = db.Column(db.String(64))
    vaccine_amount = db.Column(db.Integer) 
    reserve_amount = db.Column(db.Integer)

    def __repr__(self):
        return '<Vaccine %r>' % self.vaccine_id