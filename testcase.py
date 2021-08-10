# coding:utf-8
'''
login test case
'''
from flask import request, jsonify
import unittest
from app import app
import json

class TestCase(unittest.TestCase):
    """定義測試案例"""

    def setUp(self):
        app.testing = True  
        self.client = app.test_client()
        self.expect_result = {'identity': 'Wrong id or password!'}
        self.expect_code = 401


    def test_wrong_name_password(self):
        """測試使用者名稱或密碼錯誤"""
        
        response = self.client.post("/login", data=json.dumps({"id": 120000, "password": "xxx"}))
        resp_json = response.json
        resp_code = response.status_code
        self.assertEqual(resp_code, self.expect_code)
        self.assertEqual(resp_json, self.expect_result)

    def test_update_vaccine_task(self):
        """測試疫苗上傳時間"""

        response = self.client.post("/updateVaccine", data=json.dumps({"date": "2021-08-08", "vaccine_type": "AstraZeneca", "vaccine_amount":20}))
        resp_data = response.data
        resp_json = response.json
        resp_code = response.status_code
        self.assertEqual(resp_code, self.expect_code)


if __name__ == '__main__':
    unittest.main()