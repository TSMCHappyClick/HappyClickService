
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

result = get_find_fac_shot_rate()

with open('fac_report.json', 'w') as f:
    json.dump(result, f)