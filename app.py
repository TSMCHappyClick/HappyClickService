from flask import Flask, render_template, session  
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
import hashlib

app = Flask(__name__)
api = Api(app)

# connect to db
conn = db.connection()

# Set up session's secret key (for 加密)
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


def check_user_existence(user_id):
    user = list(conn.happyclick.UserData.find({"ID": user_id}))
    if user == []:
        return False
    return True


def return_hash(password):
    # use sha-1 to encrypt password
    sha1 = hashlib.sha1()
    sha1.update(password.encode('utf-8'))
    password_sha1_data = sha1.hexdigest()

    return password_sha1_data


@login_manager.user_loader
def load_user(user_id):
    if check_user_existence(user_id):
        curr_user = User()
        curr_user.id = user_id

        return curr_user


class login(Resource):
    def get():
        return render_template('login.html')

    def post(self):
        data = request.get_json(force=True)

        ID = int(data['ID'])
        password_before_hash = data['password']
        password = return_hash(password_before_hash)
        print('ID:{},password:{}'.format(ID, password))

        user_exist = check_user_existence(ID)
        if not user_exist:
            return jsonify({'identity': 'No user to be found!'})
        else:
            user = list(conn.happyclick.UserData.find({"ID": ID}))
            if password == user[0]['password']:

                curr_user = User()
                curr_user.id = ID
                
                session['ID'] = ID

                # 通過Flask-Login的login_user方法登入使用者
                login_user(curr_user)
                print('Succesfully login!')
                # 查看是否是醫療人員
                if ID in db.meds:
                    return jsonify({
                        'identity': 'med'
                    })
                return jsonify({
                    'identity': 'employee'
                })

            print('Login fail!')
            return jsonify({'identity': 'Wrong id or password!'})


# find staff 底下 employee 注射狀況
class find_employees_under_staff(Resource):
    def get(self):
        if session.get('ID'):
            staffs = list(conn.happyclick.StaffData.find({'ID': session.get('ID')}))
            result = {'shot': [], 'not_shot': []}

            for employeeID in staffs[0]['employees']:
                employee = list(conn.happyclick.VaccinatedData.find(
                    {'ID': int(employeeID)}))
                if employee:
                    result['shot'].append(employee[0]['ID'])
                # 將其他沒注射的加進來
                else:
                    result['not_shot'].append(employeeID)

            return result
        else:
            return jsonify({'msg':'not login yet!'})


class UpdateVaccinated(Resource):
    def post(self):
        if session.get('ID'):
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
        else:
            return jsonify({'msg':'not login yet!'})

class SearchFormData(Resource):
    def post(self):
        if session.get('ID'):
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
        else:
            return jsonify({'msg':'not login yet!'})


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
    def post(self):
        if session.get('ID'):
            # get data from frontend json
            data = request.get_json(force=True)
            # get maximum form ID from old data in DB
            largestFormId = conn.happyclick.FormData.find_one(
                sort=[("form_id", pymongo.DESCENDING)])
            formId_max = largestFormId['form_id']
            # print("\nCurrent form ID: " + str(formId_max))

            # implement json file request send to DB
            formId = formId_max + 1
            userId =    data["ID"]
            username =  data["Name"]
            vaccDate =  data["date"]
            vaccType =  data["vaccine_type"]

            if (checkVaccineAmount(vaccDate, vaccType)):
                # add data to DB
                conn.happyclick.FormData.insert_one({'form_id': formId, 'ID': int(userId),
                                                    'Name': username, 'vaccine_type': vaccType, 'date': vaccDate, 'status': False})
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
        else:
            return jsonify({'msg':'not login yet!'})


class CheckReserve(Resource):
    def post(self):
        if session.get('ID'):
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
        else:
            return jsonify({'msg':'not login yet!'})


class RemoveReserve(Resource):
    def post(self):
        if session.get('ID'):
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
        else:
            return jsonify({'msg':'not login yet!'})


class ReturnAvailable(Resource):
    def get(self):
        if session.get('ID'):
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
        else:
            return jsonify({'msg':'not login yet!'})

class UpdateVaccine(Resource):
    def post(self):
        if session.get('ID'):
            vaccine_id_dict = {"AZ": 1, "MD": 2, "BNT": 3}
            # get data from frontend json
            vaccine_data = request.get_json(force=True)
            conn.happyclick.VaccineData.insert(
                    {"vaccine_id": vaccine_id_dict[vaccine_data["vaccine_type"]], 
                    "date": vaccine_data["date"], 
                    "reserve_amount": 0,
                    "vaccine_amount": vaccine_data["vaccine_amount"],
                    "vaccine_type": vaccine_data["vaccine_type"]})
            # db_vaccine_data = conn.happyclick.VaccinatedData.find_one(
            #     {"vaccine_type": vaccine_data["vaccine_type"], "date": vaccine_data["date"]})
            # if db_vaccine_data is None:
            #     conn.happyclick.VaccinatedData.insert(
            #         {"vaccine_id": vaccine_data["ID"], "Name": vaccine_data["Name"], "vaccine_data": 0})
            # conn.happyclick.VaccinatedData.update({"vaccine_type": vaccine_data["vaccine_type"], "date": vaccine_data["date"]}, {
            #                                       "$inc": {"vaccine_amount": 1}})
            return jsonify({'msg': 'Update Vaccine successful!'})
        else:
            return jsonify({'msg':'not login yet!'})

            
@app.route('/logout')
def logout():
    if session.get('ID'):
        # delete session
        session['ID'] = False
        return jsonify({'msg': 'Logged out successfully!'})
    else:
        return jsonify({'msg': 'Not login yet!'})


api.add_resource(login, "/login")
api.add_resource(find_employees_under_staff, "/find_employees_under_staff")
api.add_resource(UpdateVaccinated, '/updateVaccinated')
api.add_resource(SearchFormData, '/searchFormdata')
api.add_resource(SaveReserve,  '/saveReserve')
api.add_resource(CheckReserve,  '/checkReserve')
api.add_resource(RemoveReserve,  '/removeReserve')
api.add_resource(ReturnAvailable, "/returnAvailable")
api.add_resource(UpdateVaccine, '/updateVaccine')

if __name__ == '__main__':
    app.run(host="localhost", port=8088, threaded=True, debug=True)
