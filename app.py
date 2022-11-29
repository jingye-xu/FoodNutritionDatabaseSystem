from flask import Flask, render_template, request, url_for, redirect
from pymongo import MongoClient
from bson.objectid import ObjectId
import pandas as pd


app = Flask(__name__)

client = MongoClient('localhost', 27018)

dbnames = client.list_database_names()

# db = client.flask_db
# todos = db.todos


@app.route('/', methods=('GET', 'POST'))
def index():
    if request.method=='POST':
        content = request.form['content']
        query = {"Main food description": {"$regex": content, "$options" :'i'}}
        search_result = food_data.find(query)
        return render_template('index.html', foods=search_result)

    all_data = food_data.find().limit(25)
    return render_template('index.html', foods=all_data)


@app.post('/<id>/delete/')
def delete(id):
    food_data.delete_one({"_id": ObjectId(id)})
    return redirect(url_for('index'))


if __name__ == "__main__":
    if "food" not in dbnames:
        db = client.food
        org_data = pd.read_csv("database.csv")
        food_data = db.data
        food_data.insert_many(org_data.to_dict("records"))
    
    db = client.food
    food_data = db.data
    app.run(debug=True, host="0.0.0.0", port=5000)