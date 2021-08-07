from flask import Flask, render_template
from flask import json
from flask.globals import request
from flask.json import jsonify
from flask_restful import Api, Resource
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
import os
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
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE')
    return response




def query_user(user_id):
    return list(conn.happyclick.UserData.find({"ID":user_id}))
    
def find_employees_under_staff(staff_id):
    staffs = list(conn.happyclick.StaffData.find({'ID':staff_id}))
    for employeeID in staffs[0]['employees']:
        # find staff 底下 employee 注射狀況
        employees = list(conn.happyclick.FormData.find({'ID':employeeID}))
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
        data = request.get_json(force = True)

        ID = int(data['ID'])
        password = data['password']
        print('ID:{},password:{}'.format(ID,password))
        
        user = query_user(ID)

        if user is not None and password == user[0]['password']:

            curr_user = User()
            curr_user.id = ID

            # 通過Flask-Login的login_user方法登入使用者Í
            login_user(curr_user)
            print('Succesfully login!')
            # 回傳true給前端去做redirect page
            if ID in db.meds:
                return jsonify ({
                    'identity':'med'
                })
            return jsonify({
                'identity' : 'employee'
            })
            
        print('Login fail!')
        return  jsonify({'identity':'Wrong id or password!'})



@login_required
@app.route('/logout')  
def logout():
    logout_user()
    return jsonify({'msg':'Logged out successfully!'})


api.add_resource(Login, "/Login")



if __name__ == '__main__':

    app.run(host="localhost", port=8088, threaded=True, debug=True)