from flask import Flask, session, render_template, url_for, redirect
from flask.globals import request
from flask.json import jsonify
from flask_restful import Api, Resource
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
import json
import os

app = Flask(__name__)
api = Api(app)
# Set up session's secret key (for 加密)
app.config['SECRET_KEY'] = os.urandom(24)
# Bundle flask and flask-login together
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.session_protection = "strong"
login_manager.login_view = 'login'
# open db
f = open('Database.json')
userdatas = json.load(f)

class User(UserMixin):
    pass

def query_user(user_id):
    for user in userdatas:
        if user_id == user['ID']:
            return user


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
        ID = data[0]['ID']
        password = data[0]['password']
        user = query_user(ID)
        if user is not None and password == user['password']:

            curr_user = User()
            curr_user.id = ID

            # 通過Flask-Login的login_user方法登入使用者
            login_user(curr_user)
            # Jump to reserve page if login
            return redirect('http://localhost:8080/HappyClick/#/reserve')

        return jsonify({'msg':'Wrong id or password!'})




class logout(Resource):
    @login_required
    def get():
        logout_user()
        return jsonify({'msg':'Logged out successfully!'})


api.add_resource(Login, "/Login")
api.add_resource(logout, "/logout")


# Closing file
f.close()

if __name__ == '__main__':
    app.run(host="localhost", port=8088, threaded=True, debug=True)
