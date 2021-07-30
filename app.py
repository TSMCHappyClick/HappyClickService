from flask import Flask, flash, redirect, url_for, session, request, logging
from flask.globals import request
from flask.json import jsonify
from flask_restful import Api, Resource
import warnings
import json
from functools import wraps


# Automatically ignore warning messages
warnings.filterwarnings('ignore')

app = Flask(__name__)
api = Api(app)

f = open('Database.json')
userdatas = json.load(f)

class Home(Resource):
    def get(self):
        print('hello world')
        return jsonify({'msg':'Hello World'})

class Login(Resource):
    def post(self):
        data = request.get_json(force = True)
        print(data)
        # todo: login verification
        find = [user for user in userdatas if user["ID"] == data["ID"]]       
        if len(find) == 0:
            return jsonify({'msg':'User not found'})
        else:
            user = find[0]
            if data['password'] == user['password']:
                return jsonify({'msg':'User {} login successfuly!'.format(user['ID'])})
                session['logged_in'] = True
                session['username'] = username
            else:
                return jsonify({'msg':'Wrong password!'})

def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Unauthorized, Please login', 'danger')
            return redirect(url_for('Login'))
    return wrap
    
class SaveReserve(Resource):
    def post(self):
        data = request.get_json(force = True)
        userId = data["ID"]
        vaccDate = data["date"]
        vaccType = data["type"]
        # TODO : Save data to server
        return jsonify({'msg':'Reserve vaccine successful!'})

class checkReserve(Resource):
    def post(self):
        data = request.get_json(force = True)
        userId = data["ID"]
        #TODO : get all reserve of this userID
        return jsonify({'msg':'Check reserve successful!'
                        , 'date':'some date'
                        , 'type':'some type'})





api.add_resource(Home, '/')
api.add_resource(Login, "/Login")
api.add_resource(SaveReserve,  '/reserve')
api.add_resource(checkReserve,  '/check')


# Closing file
f.close()

if __name__ == '__main__':
    app.run(host="localhost", port=8088, threaded=True, debug=True)
