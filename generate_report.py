
import database as db
import json
conn = db.connection()

def get_find_fac_shot_rate():
    factories = db.get_factories()
    fac_list = []
    fac_shot = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    fac_all = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
    fac_shot_rate = []
    result = {
        'factories': [],
        'rate': []
    }

    for factory in factories:
        fac_list.append(factories[factory])

    users = list(conn.happyclick.UserData.find({}))
    for user in users:
        user_vac = list(
            conn.happyclick.VaccinatedData.find({'id': user['id']}))
        if len(user_vac) == 1:
            for i in range(len(fac_list)):
                if fac_list[i] == factories[user['division']]:
                    fac_shot[i] += 1
                    fac_all[i] += 1
        else:
            for i in range(len(fac_list)):
                if fac_list[i] == factories[user['division']]:
                    fac_all[i] += 1

    for i in range(len(fac_list)):
        rate = fac_shot[i] / fac_all[i]
        fac_shot_rate.append(rate)

    result['factories'] = fac_list
    result['rate'] = fac_shot_rate

    return result


def calculation(json_result):
    json_after_cal = {
        "龍潭封測廠": 0,
        "竹科": 0,
        "中科": 0,
        "南科": 0,
        "中國": 0,
        "美國": 0,
        "新加坡": 0
    }
    for key, values in json_result.items():
        json_after_cal[key] = values[0] / values[1]

    return json_after_cal

def find_division_shot_rate():
    workers = list(conn.happyclick.UserData.find({}))
    Workers_vaccineds = list(conn.happyclick.VaccinatedData.find({}))
    divisions = db.get_divisions()
    result = {
        "龍潭封測廠": [0, 1],
        "竹科": [0, 1],
        "中科": [0, 1],
        "南科": [0, 1],
        "中國": [0, 1],
        "美國": [0, 1],
        "新加坡": [0, 1]
    }

    for worker_vaccined in Workers_vaccineds:
        workers_vac = list(conn.happyclick.UserData.find(
            {'id': worker_vaccined['id']}))
        if len(workers_vac) == 1:
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



fac_result = get_find_fac_shot_rate()
div_result = find_division_shot_rate()


with open('fac_report.json', 'w') as f:
    json.dump(fac_result, f)
with open('div_report.json', 'w') as f:
    json.dump(div_result, f)