from flask import Flask, request
from flask.globals import request
from flask.json import jsonify
from flask_restful import Api, Resource
import warnings
import json

import database as db

# Automatically ignore warning messages
warnings.filterwarnings('ignore')

app = Flask(__name__)
api = Api(app)
conn = db.connection()

class Test(Resource):
    def get(self):
        print('hello world')
        return jsonify({'msg':'Hello World'})

class UpdateVaccinated(Resource):
    def post(self):
        # get data from frontend json
        data = request.get_json(force = True)
        conn.happyclick.VaccinatedData.insert_one({"vaccinated_id":data["id"], 
                                                   "vaccinated_name":data["name"], 
                                                   "vaccine_type":data["type"],
                                                   "vaccine_date":data["date"]})
        vdata = conn.happyclick.VaccinatedData.find({"vaccinated_id":120452})
        for data in vdata:
            print(data)
        return jsonify({'msg':'Check reserve successful!'})

    def get(self):
        data = conn.happyclick.VaccinatedData.find()
        return jsonify({})


api.add_resource(UpdateVaccinated, '/UpdateVaccinated')
api.add_resource(Test, '/')

if __name__ == '__main__':
    app.run(host="localhost", port=8088, threaded=True, debug=True)
