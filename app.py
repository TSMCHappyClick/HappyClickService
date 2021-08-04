from flask import Flask, render_template
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
    

@login_manager.user_loader
def load_user(user_id):
    if query_user(user_id) is not None:
        curr_user = User()
        curr_user.id = user_id

        return curr_user


class Register(Resource):
    def post(self):
        datas = request.get_json(force=True)
        Name = datas['Name']
        ID = datas['ID']
        identity = datas['identity']
        email = datas['email']
        password = datas['password']
        division = datas['division']
        department = datas['department']

        conn.happyclick.UserData.insert_one({'Name':Name,'ID':ID,'password':password,'identity':identity,'email':email, 'division':division, 'department':department})
        print("insert user {} completed".format(ID))

        return True

class Login(Resource):
    def get():
        return render_template('login.html')
    def post(self):
        data = request.get_json(force = True)

        ID = int(data['ID'])
        password = data['password']
        print('ID:{},password:{}'.format(ID,password))

        user = query_user(ID)
        # user = query_user(password)
        if user is not None and password == user[0]['password']:

            curr_user = User()
            curr_user.id = ID

            # 通過Flask-Login的login_user方法登入使用者
            login_user(curr_user)
            print('Succesfully login!')
            # 回傳true給前端去做redirect page
            return True
            
        print('Login fail!')
        return  jsonify({'msg':'Wrong id or password!'})



@login_required
@app.route('/logout')  
def logout():
    logout_user()
    return jsonify({'msg':'Logged out successfully!'})


api.add_resource(Login, "/Login")
api.add_resource(Register, "/Register")



if __name__ == '__main__':

    app.run(host="localhost", port=8088, threaded=True, debug=True)