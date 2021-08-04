import database as db

conn = db.connection()

conn.test.user.insert_one({'name':'danny','age':20})

users = conn.test.user.find({"name":"danny"})
for user in users:
    print(user)

conn.test.user.update_one({"name":"danny"},{"$set":{"age":28}})

conn.test.user.delete_many({})