from flask import Flask, flash, redirect, url_for, session, request, logging
from flask.globals import request
from flask.json import jsonify
from flask_restful import Api, Resource
from sqlalchemy import func
import warnings
import json

from sqlalchemy.sql.expression import false, true
from db_model import db
from db_model import Userdata, Formdata, Vaccinedata

# Automatically ignore warning messages
warnings.filterwarnings('ignore')

app = Flask(__name__)
api = Api(app)

username = 'root'           
password = 'adkasghdih1919' # self pass    
host = '127.0.0.1'          
port = '3306'               
database = 'hackathon'    # self db

app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{username}:{password}@{host}:{port}/{database}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

class Home(Resource):
    def get(self):
        print('hello world')
        return jsonify({'msg':'Hello World'})


def checkVaccineAmount(vaccDate, vaccType):
    # Compare reserve and vaccine total amount to prevend out of vaccine
    vaccineRecord = Vaccinedata.query.filter_by(date=vaccDate, vaccine_type=vaccType).first()
    reserveAmount = vaccineRecord.reserve_amount
    vaccineAmount = vaccineRecord.vaccine_amount

    # print("\nCurrent vaccDate in check:{}".format(str(vaccDate)))
    # print("\nCurrent reserveAmount in check:{}".format(str(reserveAmount)))
    # print("\nCurrent vaccineAmount in check:{}".format(str(vaccineAmount)))

    if reserveAmount < vaccineAmount:
        return True # return true if reserve less than total amount
    else : 
        return False # return false if reserve equals to total amount (or other exception)

class SaveReserve(Resource):
    def post(self):
        # get data from frontend json
        data = request.get_json(force = True)
        # get maximum form ID from old data in DB
        formId_max = db.session.query(func.max(Formdata.form_id)).scalar()
        print("\nCurrent form ID: " + str(formId_max))

        # implement json file request send to DB
        formId = formId_max + 1
        userId = data["ID"]
        username = data["username"]
        vaccDate = data["vaccine_date"]
        vaccType = data["vaccine_type"]

        if (checkVaccineAmount(vaccDate, vaccType)):
            # add data to DB
            newReserve = Formdata(form_id=formId, user_id=userId, username=username, vaccine_type=vaccType, vaccine_date=vaccDate)
            db.session.add_all([newReserve])
            db.session.commit()
            # update reserve amount
            reserveSelected = Vaccinedata.query.filter_by(vaccine_type=vaccType, date=vaccDate).first()
            reserveSelected.reserve_amount += 1
            db.session.commit()
            # TODO : handle exception
            return jsonify({'msg':'Reservation of vaccine successful!'})
        else :
            return jsonify({'msg':'Reservation chosen is full!'})

class CheckReserve(Resource):
    def post(self):
        data = request.get_json(force = True)
        userId = data["ID"]
        reserveRecord = Formdata.query.filter_by(user_id=userId).first()
        print("\nvaccine type: "+reserveRecord.vaccine_type+", vaccine date: "+str(reserveRecord.vaccine_date))
        print(type(reserveRecord))
        vaccine_type = reserveRecord.vaccine_type
        vaccine_date = reserveRecord.vaccine_date
        return jsonify({'msg':'Check reserve successful!'
                        , 'vaccine_type': vaccine_type
                        , 'vaccine_date': str(vaccine_date)})

class RemoveReserve(Resource):
    def post(self):
        # get data from frontend json
        data = request.get_json(force = True)
        userId = data["ID"]
        vaccDate = data["vaccine_date"]
        vaccType = data["vaccine_type"]
        # send request to delete data in DB
        reserveRecord = Formdata.query.filter_by(user_id=userId, vaccine_date=vaccDate, vaccine_type=vaccType).first()
        db.session.delete(reserveRecord)
        db.session.commit()
        # update reserve amount
        vaccineRecord = Vaccinedata.query.filter_by(date=vaccDate, vaccine_type=vaccType).first()
        vaccineRecord.reserve_amount -= 1
        db.session.commit()
        return jsonify({'msg': 'Reservation removed successfully!'})

class ReturnAvailable(Resource):
    def get(self):
        # query DB for all vaccine record, and remove those are full
        vaccineAvailable = Vaccinedata.query.all()
        availableList = [x for x in vaccineAvailable if x.vaccine_amount > x.reserve_amount]
        # implement json file of remaining vaccine for frontend
        returnList = []
        for i in availableList:
            vaccineDict = {'vaccine_date': str(i.date),
                            'vaccine_type': i.vaccine_type,
                            'vaccine_remaining': i.vaccine_amount - i.reserve_amount}
            returnList.append(vaccineDict)
        return jsonify(returnList)



api.add_resource(Home, '/')
# api.add_resource(Login, "/Login")
api.add_resource(SaveReserve,  '/Reserve')
api.add_resource(CheckReserve,  '/Check')
api.add_resource(RemoveReserve,  '/Remove')
api.add_resource(ReturnAvailable, "/ReturnAvailable")


if __name__ == '__main__':
    app.run(host="localhost", port=8088, threaded=True, debug=True)