'''
2021/07/31 test flask_sqlalchemy
usage : from db_model import db
        from db_model import Userdata, Formdata, Vaccinedata

        db.create_all()
        user1 = Userdata(ID=111111, Name='hehe', password='happyclick', identity="it engineer", email="hehe@gmail.com")
        db.session.add_all([user1])
        db.session.commit()
        user = Userdata.query.all()
        for i in user:
            print(i.ID, i.Name)

db_config.ini usage : import configparser

                      config = configparser.ConfigParser()
                      config.read('db_config.ini')
                      print(config["database"]["username"]) ==> 'root'
'''

from typing import DefaultDict
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class UserData(db.Model):
    __tablename__ = 'userdata'
    ID = db.Column(db.Integer, primary_key=True) 
    Name = db.Column(db.String(64)) 
    password = db.Column(db.String(64))
    identity = db.Column(db.String(64))
    email = db.Column(db.String(64), unique=True)
    division = db.Column(db.String(64))

    def __repr__(self):
        return "<Userdata %r>" % self.ID

class FormData(db.Model):
    __tablename__ = 'formdata'
    form_id = db.Column(db.Integer, primary_key=True) 
    user_id = db.Column(db.Integer) 
    username = db.Column(db.String(64))
    vaccine_type = db.Column(db.String(64))
    vaccine_date = db.Column(db.Date)

    def __repr__(self):
        return "<Formdata %r>" % self.form_id

class VaccineData(db.Model):
    __tablename__ = 'vaccinedata' 
    vaccine_id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date) 
    vaccine_type = db.Column(db.String(64))
    vaccine_amount = db.Column(db.Integer) 

    def __repr__(self):
        return '<Vaccinedata %r>' % self.vaccine_id

class VaccinatedData(db.Model):
    __tablename__ = 'userdata'
    vaccinated_id = db.Column(db.Integer, primary_key=True) 
    vaccinated_name = db.Column(db.String(64)) 
    vaccine_type = db.Column(db.String(64), default="Null")
    vaccine_date = db.Column(db.Date)

    def __repr__(self):
        return "<VaccinatedData %r>" % self.vaccinated_id