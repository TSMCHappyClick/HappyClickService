from flask import Flask, render_template
from flask.globals import request
from flask.json import jsonify
from flask_restful import Api, Resource
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
import os
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
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE')
    return response




def check_user_existence(user_id):
    user = list(conn.happyclick.UserData.find({"ID":user_id}))
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
        data = request.get_json(force = True)

        ID = int(data['ID'])
        password_before_hash = data['password']
        password = return_hash(password_before_hash)
        print('ID:{},password:{}'.format(ID,password))
        
        user_exist = check_user_existence(ID)
        if not user_exist:
            return  jsonify({'identity':'No user to be found!'})
        else:
            user = list(conn.happyclick.UserData.find({"ID":ID}))
            if password == user[0]['password']:

                curr_user = User()
                curr_user.id = ID

                # 通過Flask-Login的login_user方法登入使用者
                login_user(curr_user)
                print('Succesfully login!')
                # 查看是否是醫療人員
                if ID in db.meds:
                    return jsonify ({
                        'identity':'med'
                    })
                return jsonify({
                    'identity' : 'employee'
                })
                
            print('Login fail!')
            return  jsonify({'identity':'Wrong id or password!'})


# find staff 底下 employee 注射狀況
class find_employees_under_staff(Resource):
    def get(self):

        staffs = list(conn.happyclick.StaffData.find({'ID':current_user.id}))
        result = {'shot':[],'not_shot':[]}

        for employeeID in staffs[0]['employees']:
            employee = list(conn.happyclick.VaccinatedData.find({'ID':int(employeeID)}))
            if employee:
                result['shot'].append(employee[0]['ID'])
            # 將其他沒注射的加進來
            else:
                result['not_shot'].append(employeeID)

        return result



@login_required
@app.route('/logout')  
def logout():
    logout_user()
    return jsonify({'msg':'Logged out successfully!'})


api.add_resource(login, "/login")
api.add_resource(find_employees_under_staff, "/find_employees_under_staff")



if __name__ == '__main__':

    app.run(host="localhost", port=8088, threaded=True, debug=True)