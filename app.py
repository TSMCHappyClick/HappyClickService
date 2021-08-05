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

class UpdateVaccinated(Resource):
    def post(self):
        # get data from frontend json
        vaccinated_data = request.get_json(force = True)
        conn.happyclick.FormData.update_one({"form_id" : vaccinated_data["form_id"]},{"$set" : {"status" : True}})
        db_vaccinated_data = conn.happyclick.VaccinatedData.find_one({"ID" : vaccinated_data["ID"]})
        if db_vaccinated_data is None:
            conn.happyclick.VaccinatedData.insert({"ID" : vaccinated_data["ID"] ,"Name" : vaccinated_data["Name"], "vaccinated_times" : 0})
        conn.happyclick.VaccinatedData.update({"ID" : vaccinated_data["ID"]}, {"$inc" : {"vaccinated_times" : 1}})
        return jsonify({'msg' : 'Update Vaccinated successful!'})

class SearchFormData(Resource):
    def post(self):
        datas_to_front = []
        date_data = request.get_json(force = True)
        datas_from_db = conn.happyclick.FormData.find({"date" : date_data["date"], "status" : False})
        for data in datas_from_db:
            formData_dict = {"form_id" : data["form_id"], 
                            'vaccine_type' : data['vaccine_type'],
                            'ID' : data['ID'],
                            "Name" : str(data["Name"])}
            datas_to_front.append(formData_dict)

        if len(datas_to_front) == 0:
            return jsonify({'msg' : 'No FormData data!'})
        return jsonify(datas_to_front)

api.add_resource(UpdateVaccinated, '/UpdateVaccinated')
api.add_resource(SearchFormData, '/SearchFormData')

if __name__ == '__main__':
    app.run(host="localhost", port=8088, threaded=True, debug=True)
