from flask import Flask, render_template
from flask import json
from flask.globals import request
from flask.json import jsonify
from flask_restful import Api, Resource
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
import os
from flask_pymongo import PyMongo
import pymongo
from datetime import datetime
import database as db

app = Flask(__name__)
api = Api(app)

# connect to db
conn = db.connection()

# Set up session's secret key (for 加密) and load database config
app.config['SECRET_KEY'] = os.urandom(24)

# Bundle flask and flask-login together
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.session_protection = "strong"
login_manager.login_view = 'login'


class User(UserMixin):
    pass


@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers',
                         'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE')
    return response


def query_user(user_id):
    return list(conn.happyclick.UserData.find({"ID": user_id}))


def find_employees_under_staff(staff_id):
    staffs = list(conn.happyclick.StaffData.find({'ID': staff_id}))
    for employeeID in staffs[0]['employees']:
        # find staff 底下 employee 注射狀況
        employees = list(conn.happyclick.FormData.find({'ID': employeeID}))
        for employee in employees:
            if employee['status']:
                print(employee)


@login_manager.user_loader
def load_user(user_id):
    if query_user(user_id) is not None:
        curr_user = User()
        curr_user.id = user_id

        return curr_user


class Login(Resource):
    def get():
        return render_template('login.html')

    def post(self):
        data = request.get_json(force=True)

        ID = int(data['ID'])
        password = data['password']
        print('ID:{},password:{}'.format(ID, password))

        user = query_user(ID)

        if user is not None and password == user[0]['password']:

            curr_user = User()
            curr_user.id = ID

            # 通過Flask-Login的login_user方法登入使用者Í
            login_user(curr_user)
            print('Succesfully login!')
            # 回傳true給前端去做redirect page
            if ID in db.meds:
                return jsonify({
                    'identity': 'med'
                })
            return jsonify({
                'identity': 'employee'
            })

        print('Login fail!')
        return jsonify({'identity': 'Wrong id or password!'})


class UpdateVaccinated(Resource):
    def post(self):
        # get data from frontend json
        vaccinated_data = request.get_json(force=True)
        conn.happyclick.FormData.update_one(
            {"form_id": int(vaccinated_data["form_id"])}, {"$set": {"status": True}})
        db_vaccinated_data = conn.happyclick.VaccinatedData.find_one(
            {"ID": int(vaccinated_data["ID"])})
        if db_vaccinated_data is None:
            conn.happyclick.VaccinatedData.insert(
                {"ID": vaccinated_data["ID"], "Name": vaccinated_data["Name"], "vaccinated_times": 0})
        conn.happyclick.VaccinatedData.update({"ID": vaccinated_data["ID"]}, {
                                              "$inc": {"vaccinated_times": 1}})
        return jsonify({'msg': 'Update Vaccinated successful!'})


class SearchFormData(Resource):
    def post(self):
        datas_to_front = []
        date_data = request.get_json(force=True)
        datas_from_db = conn.happyclick.FormData.find(
            {"date": date_data["date"], "status": False})
        for data in datas_from_db:
            formData_dict = {"form_id": data["form_id"],
                             'vaccine_type': data['vaccine_type'],
                             'ID': data['ID'],
                             "Name": str(data["Name"])}
            datas_to_front.append(formData_dict)

        if len(datas_to_front) == 0:
            return jsonify({'msg': 'No FormData data!'})
        return jsonify(datas_to_front)


def checkVaccineAmount(vaccDate, vaccType):
    # Compare reserve and vaccine total amount to prevend out of vaccine
    vaccineRecord = conn.happyclick.VaccineData.find_one(
        {'date': vaccDate, 'vaccine_type': vaccType})
    reserveAmount = vaccineRecord['reserve_amount']
    vaccineAmount = vaccineRecord['vaccine_amount']

    if reserveAmount < vaccineAmount:
        return True  # return true if reserve less than total amount
    else:
        # return false if reserve equals to total amount (or other exception)
        return False


class SaveReserve(Resource):
    @login_required
    def post(self):
        # get data from frontend json
        data = request.get_json(force=True)
        # get maximum form ID from old data in DB
        largestFormId = conn.happyclick.FormData.find_one(
            sort=[("form_id", pymongo.DESCENDING)])
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
            conn.happyclick.FormData.insert_one({'form_id': formId, 'ID': int(
                userId), 'Name': username, 'vaccine_type': vaccType, 'date': vaccDate, 'status': False})
            # update reserve amount
            vaccineRecord = conn.happyclick.VaccineData.find_one(
                {'date': vaccDate, 'vaccine_type': vaccType})
            conn.happyclick.VaccineData.update_one({'date': vaccDate, 'vaccine_type': vaccType},
                                                   {'$set': {
                                                       "reserve_amount": vaccineRecord['reserve_amount'] + 1}},
                                                   upsert=False)
            # TODO : handle exception
            return jsonify({'msg': 'Reservation of vaccine successful!'})
        else:
            return jsonify({'msg': 'Reservation chosen is full!'})


class CheckReserve(Resource):
    @login_required
    def post(self):
        data = request.get_json(force=True)
        userId = data["ID"]
        reserveRecord = conn.happyclick.FormData.find_one(
            {'ID': int(userId), 'status': False})  # prevend DB from query vaccinated record
        if reserveRecord:
            print('\nFind one unvaccinated reserve!')
            vaccine_type = reserveRecord['vaccine_type']
            vaccine_date = reserveRecord['date']
            return jsonify({'msg': 'Check reserve successful!', 'vaccine_type': vaccine_type, 'date': vaccine_date})
        else:
            return jsonify({'msg': 'No reservation found!'})


class RemoveReserve(Resource):
    @login_required
    def post(self):
        # get data from frontend json
        data = request.get_json(force=True)
        userId = data["ID"]
        vaccDate = data["date"]
        vaccType = data["vaccine_type"]
        # send request to delete data in DB
        reserveRecord = conn.happyclick.FormData.find_one(
            {'ID': int(userId), 'date': vaccDate, 'vaccine_type': vaccType, 'status': False})
        if reserveRecord:
            print('\nFind one unvaccinated reserve!')
            conn.happyclick.FormData.delete_one(
                {'ID': userId, 'date': vaccDate, 'vaccine_type': vaccType})
            # update reserve amount
            vaccineRecord = conn.happyclick.VaccineData.find_one(
                {'date': vaccDate, 'vaccine_type': vaccType})
            conn.happyclick.VaccineData.update_one({'date': vaccDate, 'vaccine_type': vaccType},
                                                   {'$set': {
                                                       "reserve_amount": vaccineRecord['reserve_amount'] - 1}},
                                                   upsert=False)
            return jsonify({'msg': 'Reservation removed successfully!'})
        else:
            return jsonify({'msg': 'No reservation found!'})


class ReturnAvailable(Resource):
    def get(self):
        # query DB for all vaccine record, and remove those are full
        vaccineAvailable = conn.happyclick.VaccineData.find({})
        availableList = [
            x for x in vaccineAvailable if x['vaccine_amount'] > x['reserve_amount']]
        # implement json file of remaining vaccine for frontend
        returnList = []
        for i in availableList:
            vaccineDict = {'date': i['date'],
                           'vaccine_type': i['vaccine_type'],
                           'vaccine_remaining': i['vaccine_amount'] - i['reserve_amount']}
            returnList.append(vaccineDict)
        return jsonify(returnList)


@login_required
@app.route('/logout')
def logout():
    logout_user()
    return jsonify({'msg': 'Logged out successfully!'})


api.add_resource(Login, "/Login")
api.add_resource(UpdateVaccinated, '/UpdateVaccinated')
api.add_resource(SearchFormData, '/SearchFormData')
api.add_resource(SaveReserve,  '/Reserve')
api.add_resource(CheckReserve,  '/Check')
api.add_resource(RemoveReserve,  '/Remove')
api.add_resource(ReturnAvailable, "/ReturnAvailable")

if __name__ == '__main__':
    app.run(host="localhost", port=8088, threaded=True, debug=True)
