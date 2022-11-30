from flask import Flask, render_template, request, url_for, redirect
from pymongo import MongoClient
from bson.objectid import ObjectId
import pandas as pd
from os.path import exists
import sys
import local_config

app = Flask(__name__)

client = MongoClient(local_config.database_ip, int(local_config.database_port))

dbnames = client.list_database_names()

@app.route('/', methods=('GET', 'POST'))
def index():
    # handle the search function
    if request.method=='POST':
        content = request.form['content'].split(" ")
        and_list = []
        for i in content:
            and_list.append({"Main food description": {"$regex": i, "$options" :'i'}})
        query = {"$and": and_list}
        search_result = food_data.find(query)
        return render_template('index.html', foods=search_result)

    all_data = food_data.find().limit(25)
    return render_template('index.html', foods=all_data)


@app.post('/<id>/delete/')
def delete(id):
    food_data.delete_one({"_id": ObjectId(id)})
    return redirect(url_for('index'))


if __name__ == "__main__":

    # check if self-signed certificates exist
    if not exists("cert.pem") or not exists("key.pem"):
        print("Does not find self-signed certificates, run command below in your terminal:")
        print("openssl req -x509 -newkey rsa:4096 -nodes -out cert.pem -keyout key.pem -days 365")
        sys.exit(1)

    # check if database exists
    if "food" not in dbnames:
        db = client.food
        org_data = pd.read_csv("database.csv")
        food_data = db.data
        food_data.insert_many(org_data.to_dict("records"))
    
    db = client.food
    food_data = db.data
    app.run(debug=True, host="0.0.0.0", port=int(local_config.webserver_port), ssl_context=('cert.pem', 'key.pem'))
