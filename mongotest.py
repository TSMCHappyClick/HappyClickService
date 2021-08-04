import database as db

conn = db.connection()

conn.happyclick.VaccineData.insert_one({'vaccine_id':0, 'date':20})

users = conn.test.user.find_one({"name":"danny"})
print(users)
# for user in users:
#     print(user['name'])

# conn.test.user.update_one({"name":"danny"},{"$set":{"age":28}})

# conn.test.user.delete_many({})