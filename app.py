from flask import Flask, flash, redirect, url_for, session, request, logging
from flask.globals import request
from flask.json import jsonify
from flask_restful import Api, Resource
from sqlalchemy import func
import warnings
import json
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
# f = open('Database.json')
# userdatas = json.load(f)


class Home(Resource):
    def get(self):
        print('hello world')
        return jsonify({'msg':'Hello World'})

# class Login(Resource):
#     def post(self):
#         data = request.get_json(force = True)
#         print(data)
#         # todo: login verification
#         find = [user for user in userdatas if user["ID"] == data["ID"]]       
#         if len(find) == 0:
#             return jsonify({'msg':'User not found'})
#         else:
#             user = find[0]
#             if data['password'] == user['password']:
#                 return jsonify({'msg':'User {} login successfuly!'.format(user['ID'])})
#             else:
#                 return jsonify({'msg':'Wrong password!'})
    
class SaveReserve(Resource):
    def post(self):
        data = request.get_json(force = True)
        formId_max = db.session.query(func.max(Formdata.form_id)).scalar()
        # users = db.session.query(User).filter(User.numLogins == max_logins).all()
        print("\nCurrent form ID: " + formId_max)
        formId = formId_max + 1
        userId = data["ID"]
        username = data["username"]
        vaccDate = data["vaccine_date"]
        vaccType = data["vaccine_type"]

        newReserve = Formdata(form_id=formId, user_id=userId, username=username, vaccine_type=vaccType, vaccine_date=vaccDate)
        db.session.add_all([newReserve])
        db.session.commit()
        # TODO : handle exception
        return jsonify({'msg':'Reserve vaccine successful!'})

class CheckReserve(Resource):
    def post(self):
        data = request.get_json(force = True)
        userId = data["ID"]
        #TODO : get all reserve of this userID
        reserveRecord = Formdata.query.filter_by(user_id=userId).first()
        print("\nvaccine type: "+reserveRecord.vaccine_type+", vaccine date: "+reserveRecord.vaccine_date)
        vaccine_type = reserveRecord.vaccine_type
        vaccine_date = reserveRecord.vaccine_date
        return jsonify({'msg':'Check reserve successful!'
                        , 'vaccine_type': vaccine_type
                        , 'vaccine_date': vaccine_date})

class RemoveReserve(Resource):
    def post(self):
        data = request.get_json(force = True)
        userId = data["ID"]
        vaccDate = data["vaccine_date"]
        vaccType = data["vaccine_type"]
        # TODO : remove select reservation in DB
        reserveRecord = Formdata.query.filter_by(user_id=userId, vaccine_date=vaccDate, vaccine_type=vaccType).first()
        db.session.delete(reserveRecord)
        db.session.commit()
        return jsonify({'msg': 'Reservation removed successfully!'})

class AvailableDate(Resource):
    def get(self):
        print("Return available date for reserve.")
        # TODO : check if reservation is full
        # TODO : get available date and type
        return jsonify({})






api.add_resource(Home, '/')
# api.add_resource(Login, "/Login")
api.add_resource(SaveReserve,  '/Reserve')
api.add_resource(CheckReserve,  '/Check')
api.add_resource(RemoveReserve,  '/Remove')
api.add_resource(AvailableDate, "/AvailableCheck")

# Closing file
# f.close()

if __name__ == '__main__':
    app.run(host="localhost", port=8088, threaded=True, debug=True)
