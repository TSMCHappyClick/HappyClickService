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
    user = list(conn.happyclick.UserData.find({"id": user_id}))
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

        ID = int(data['id'])
        password_before_hash = data['password']
        password = return_hash(password_before_hash)
        print('id:{},password:{}'.format(ID, password))

        user_exist = check_user_existence(ID)
        if not user_exist:
            return jsonify({'identity': 'No user to be found!'})
        else:
            user = list(conn.happyclick.UserData.find({"id": ID}))
            if password == user[0]['password']:

                curr_user = User()
                curr_user.id = ID
                
                session['id'] = ID

                # 通過Flask-Login的login_user方法登入使用者
                # login_user(curr_user)
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
        if session.get('id'):
            staffs = list(conn.happyclick.StaffData.find({'id': session.get('id')}))
            result = {'shot': [], 'not_shot': []}

            for employeeID in staffs[0]['employees']:
                employee = list(conn.happyclick.VaccinatedData.find(
                    {'id': int(employeeID)}))
                if employee:
                    result['shot'].append(employee[0]['id'])
                # 將其他沒注射的加進來
                else:
                    result['not_shot'].append(employeeID)

            return result
        else:
            return jsonify({'msg':'not login yet!'})


class UpdateVaccinated(Resource):
    def post(self):
        if session.get('id'):
        # get data from frontend json
            vaccinated_data = request.get_json(force=True)
            conn.happyclick.FormData.update_one(
                {"form_id": int(vaccinated_data["form_id"])}, {"$set": {"status": True}})
            db_vaccinated_data = conn.happyclick.VaccinatedData.find_one(
                {"id": int(vaccinated_data["id"])})
            if db_vaccinated_data is None:
                conn.happyclick.VaccinatedData.insert(
                    {"id": vaccinated_data["id"], "username": vaccinated_data["username"], "vaccinated_times": 0})
            conn.happyclick.VaccinatedData.update({"id": vaccinated_data["id"]}, {
                                                "$inc": {"vaccinated_times": 1}})
            return jsonify({'msg': 'Update Vaccinated successful!'})
        else:
            return jsonify({'msg':'not login yet!'})

class SearchFormData(Resource):
    def post(self):
        if session.get('id'):
            datas_to_front = []
            date_data = request.get_json(force=True)
            datas_from_db = conn.happyclick.FormData.find(
                {"date": date_data["date"], "status": False})
            for data in datas_from_db:
                formData_dict = {"form_id": data["form_id"],
                                'vaccine_type': data['vaccine_type'],
                                'id': data['id'],
                                "username": str(data["username"])}
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
        if session.get('id'):
            # get data from frontend json
            data = request.get_json(force=True)
            # get maximum form ID from old data in DB
            largestFormId = conn.happyclick.FormData.find_one(
                sort=[("form_id", pymongo.DESCENDING)])
            formId_max = largestFormId['form_id']

            # implement json file request send to DB
            formId = formId_max + 1
            userId =    data["id"]
            username =  data["username"]
            vaccDate =  data["date"]
            vaccType =  data["vaccine_type"]

            if (checkVaccineAmount(vaccDate, vaccType)):
                # add data to DB
                conn.happyclick.FormData.insert_one({'form_id': formId, 'id': int(userId),
                                                    'username': username, 'vaccine_type': vaccType, 'date': vaccDate, 'status': False})
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
    def get(self):
        if session.get('id'):
            userId = request.args.get('id', default="999999", type=str)
            reserveRecord = conn.happyclick.FormData.find_one(
                {'id': int(userId), 'status': False})  # prevend DB from query vaccinated record
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
        if session.get('id'):
            # get data from frontend json
            data = request.get_json(force=True)
            userId = data["id"]
            vaccDate = data["date"]
            vaccType = data["vaccine_type"]
            # send request to delete data in DB
            reserveRecord = conn.happyclick.FormData.find_one(
                {'id': int(userId), 'date': vaccDate, 'vaccine_type': vaccType, 'status': False})
            if reserveRecord:
                print('\nFind one unvaccinated reserve!')
                conn.happyclick.FormData.delete_one(
                    {'id': int(userId), 'date': vaccDate, 'vaccine_type': vaccType})
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
        print(session.get('id'))
        if session.get('id'):
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
        if session.get('id'):
            vaccine_id_dict = {"AstraZeneca": 1, "Moderna": 2, "BioNTech": 3}
            # get data from frontend json
            vaccine_data = request.get_json(force=True)
            db_vaccine_data = conn.happyclick.VaccineData.find_one(
                {"vaccine_type": vaccine_data["vaccine_type"], "date": vaccine_data["date"]})
            if db_vaccine_data is None:
                conn.happyclick.VaccineData.insert(
                        {"vaccine_id": vaccine_id_dict[vaccine_data["vaccine_type"]], 
                        "date": vaccine_data["date"], 
                        "reserve_amount": 0,
                        "vaccine_amount": 0,
                        "vaccine_type": vaccine_data["vaccine_type"]})
            for num in range(vaccine_data["vaccine_amount"]):
                conn.happyclick.VaccineData.update({"vaccine_type": vaccine_data["vaccine_type"], "date": vaccine_data["date"]}, {
                                                    "$inc": {"vaccine_amount": 1}})
            return jsonify({'msg': 'Update Vaccine successful!'})
        else:
            return jsonify({'msg':'not login yet!'})

def calculation(json_result):
    json_after_cal = {
        "竹科":0,
        "中科":0,
        "南科":0,
        "中國":0,
        "美國":0,
        "新加坡":0,
        "龍潭封測廠":0
    }
    for key, values in json_result.items():
        json_after_cal[key] = values[0] / values[1]

    return json_after_cal

class find_division_shot_rate(Resource):
    def get(self):
        if session.get('id'):
            workers = list(conn.happyclick.UserData.find({}))
            Workers_vaccineds = list(conn.happyclick.VaccinatedData.find({}))
            divisions = db.get_divisions()
            result = {
                "竹科":[0,0],
                "中科":[0,0],
                "南科":[0,0],
                "中國":[0,0],
                "美國":[0,0],
                "新加坡":[0,0],
                "龍潭封測廠":[0,0]
            }

            for worker_vaccined in Workers_vaccineds:
                workers_vac = list(conn.happyclick.UserData.find({'id': worker_vaccined['id'] }))
                if len(workers_vac) == 1 :
                    for key, value in divisions.items():
                        for i in range(len(value)):
                            if value[i] == workers_vac[0]['division']:
                                result[key][0] += 1


            for key, value in divisions.items():
                for i in range(len(value)):
                    for worker in workers:
                        if value[i] == worker['division']:
                            result[key][1] += 1
            
            print(result)
            result = calculation(result)
            return result
        else:
            return jsonify({'msg':'not login yet!'})


@app.route('/logout')
def logout():
    if session.get('id'):
        # delete session
        session['id'] = False
        return jsonify({'msg': 'Logged out successfully!'})
    else:
        return jsonify({'msg': 'Not login yet!'})


api.add_resource(login, "/login")
api.add_resource(find_employees_under_staff, "/find_employees_under_staff")
api.add_resource(find_division_shot_rate, "/find_division_shot_rate")
api.add_resource(UpdateVaccinated, '/updateVaccinated')
api.add_resource(SearchFormData, '/searchFormdata')
api.add_resource(SaveReserve,  '/saveReserve')
api.add_resource(CheckReserve,  '/checkReserve')
api.add_resource(RemoveReserve,  '/removeReserve')
api.add_resource(ReturnAvailable, "/returnAvailable")
api.add_resource(UpdateVaccine, '/updateVaccine')

if __name__ == '__main__':
    app.run(host="localhost", port=8088, threaded=True, debug=True)
