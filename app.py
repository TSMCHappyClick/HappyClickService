from dns.rdatatype import NULL
from flask import Flask, flash, redirect, url_for, session, request, logging
from flask.globals import request
from flask.json import jsonify
from flask_restful import Api, Resource
from flask_pymongo import PyMongo
import pymongo
from sqlalchemy import func
import warnings
import json
from datetime import datetime
from sqlalchemy.sql.elements import Null

from sqlalchemy.sql.expression import null

import database as db

# Automatically ignore warning messages
warnings.filterwarnings('ignore')

app = Flask(__name__)
api = Api(app)
# 1. Maria DB
# username = 'root'           
# password = 'adkasghdih1919' # self pass    
# host = '127.0.0.1'          
# port = '3306'               
# database = 'hackathon'    # self db

# app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{username}:{password}@{host}:{port}/{database}'
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# db.init_app(app)

# 2. Mongo DB
conn = db.connection()


class Home(Resource):
    def get(self):
        print('hello world')
        return jsonify({'msg':'Hello World'})


def checkVaccineAmount(vaccDate, vaccType):
    # Compare reserve and vaccine total amount to prevend out of vaccine
    vaccineRecord = conn.happyclick.VaccineData.find_one({'date': vaccDate, 'vaccine_type': vaccType})
    reserveAmount = vaccineRecord['reserve_amount']
    vaccineAmount = vaccineRecord['vaccine_amount']

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
        largestFormId = conn.happyclick.FormData.find_one(sort=[("form_id", pymongo.DESCENDING)])
        formId_max = largestFormId['form_id']
        # print("\nCurrent form ID: " + str(formId_max))

        # implement json file request send to DB
        formId = formId_max + 1
        userId = data["ID"]
        username = data["Name"]
        vaccDate = data["date"]
        vaccType = data["vaccine_type"]

        if (checkVaccineAmount(vaccDate, vaccType)):
            # add data to DB
            conn.happyclick.FormData.insert_one({'form_id': formId, 'ID': userId, 'Name': username, 'vaccine_type': vaccType, 'date': vaccDate, 'status': False})
            # update reserve amount
            vaccineRecord = conn.happyclick.VaccineData.find_one({'date': vaccDate, 'vaccine_type': vaccType})
            conn.happyclick.VaccineData.update_one({'date': vaccDate, 'vaccine_type': vaccType}, 
                                                {'$set': {"reserve_amount": vaccineRecord['reserve_amount'] + 1}}, 
                                                upsert=False)
            # TODO : handle exception
            return jsonify({'msg':'Reservation of vaccine successful!'})
        else :
            return jsonify({'msg':'Reservation chosen is full!'})

class CheckReserve(Resource):
    def post(self):
        data = request.get_json(force = True)
        userId = data["ID"]
        reserveRecord = conn.happyclick.FormData.find_one({'ID': userId, 'status': False}) # prevend DB from query vaccinated record
        if reserveRecord :
            print('\nFind one unvaccinated reserve!')
            vaccine_type = reserveRecord['vaccine_type']
            vaccine_date = reserveRecord['date']
            return jsonify({'msg':'Check reserve successful!'
                            , 'vaccine_type': vaccine_type
                            , 'date': vaccine_date})
        else:
            return jsonify({'msg': 'No reservation found!'})

class RemoveReserve(Resource):
    def post(self):
        # get data from frontend json
        data = request.get_json(force = True)
        userId = data["ID"]
        vaccDate = data["date"]
        vaccType = data["vaccine_type"]
        # send request to delete data in DB
        reserveRecord = conn.happyclick.FormData.find_one({'ID': userId, 'date': vaccDate, 'vaccine_type': vaccType, 'status': False})
        if reserveRecord:
            print('\nFind one unvaccinated reserve!')
            conn.happyclick.FormData.delete_one({'ID': userId, 'date': vaccDate, 'vaccine_type': vaccType})
            # update reserve amount
            vaccineRecord = conn.happyclick.VaccineData.find_one({'date': vaccDate, 'vaccine_type': vaccType})
            conn.happyclick.VaccineData.update_one({'date': vaccDate, 'vaccine_type': vaccType}, 
                                                    {'$set': {"reserve_amount": vaccineRecord['reserve_amount'] - 1}}, 
                                                    upsert=False)
            return jsonify({'msg': 'Reservation removed successfully!'})
        else:
            return jsonify({'msg': 'No reservation found!'})

class ReturnAvailable(Resource):
    def get(self):
        # query DB for all vaccine record, and remove those are full
        vaccineAvailable = conn.happyclick.VaccineData.find({})
        availableList = [x for x in vaccineAvailable if x['vaccine_amount'] > x['reserve_amount']]
        # implement json file of remaining vaccine for frontend
        returnList = []
        for i in availableList:
            vaccineDict = {'date': i['date'],
                            'vaccine_type': i['vaccine_type'],
                            'vaccine_remaining': i['vaccine_amount'] - i['reserve_amount']}
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