from flask import Flask, render_template, request, url_for, redirect
from pymongo import MongoClient
from bson.objectid import ObjectId
import pandas as pd
from os.path import exists
import sys
import local_config
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError
from flask_bcrypt import Bcrypt


app = Flask(__name__)
# username and password stores inside docker instead of mongodb
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = local_config.session_key
passdb = SQLAlchemy(app)
bcrypt = Bcrypt(app)


client = MongoClient(local_config.database_ip, int(local_config.database_port))
dbnames = client.list_database_names()

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(passdb.Model, UserMixin):
    id = passdb.Column(passdb.Integer, primary_key=True)
    username = passdb.Column(passdb.String(20), nullable=False, unique=True)
    password = passdb.Column(passdb.String(80), nullable=False)


class RegisterForm(FlaskForm):
    username = StringField(validators=[
                           InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username"})

    password = PasswordField(validators=[
                             InputRequired(), Length(min=8, max=20)], render_kw={"placeholder": "Password"})

    submit = SubmitField('Signup')

    def validate_username(self, username):
        existing_user_username = User.query.filter_by(
            username=username.data).first()
        if existing_user_username:
            raise ValidationError(
                'That username already exists. Please choose a different one.')


class LoginForm(FlaskForm):
    username = StringField(validators=[
                           InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username"})

    password = PasswordField(validators=[
                             InputRequired(), Length(min=8, max=20)], render_kw={"placeholder": "Password"})

    submit = SubmitField('Login')


@app.route('/', methods=('GET', 'POST'))
def index():
    # handle the search function
    if request.method=='POST':
        content = request.form['content']
        query = {"Main food description": {"$regex": content, "$options" :'i'}}
        search_result = food_data.find(query).limit(25)
        return render_template('index.html', foods=search_result)

    all_data = food_data.find().limit(25)
    return render_template('index.html', foods=all_data)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user)
                return redirect(url_for('advance'))
    return render_template('login.html', form=form)


@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


@ app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = RegisterForm()

    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data)
        new_user = User(username=form.username.data, password=hashed_password)
        passdb.session.add(new_user)
        passdb.session.commit()
        return redirect(url_for('login'))

    return render_template('signup.html', form=form)


@app.route('/advance', methods=['GET', 'POST'])
@login_required
def advance(weight=100):
    # handle the search function
    if request.method=='POST':
        content = request.form['content'].split(" ")
        weight = int(request.form['weight'])
        and_list = []
        for i in content:
            and_list.append({"Main food description": {"$regex": i, "$options" :'i'}})
        query = {"$and": and_list}
        search_result = food_data.find(query).limit(25)
        return render_template('advance.html', foods=search_result, scale=weight)

    all_data = food_data.find().limit(25)
    return render_template('advance.html', foods=all_data, scale=weight)


@app.route('/addfood', methods=['GET', 'POST'])
@login_required
def addfood():
    # handle the search function
    if request.method=='POST':
        scale = float(request.form["weight"])
        new_food = {
            "Food code": request.form["foodcode"],
            "Main food description": request.form["description"],
            "WWEIA number": request.form["wweia_number"],
            "WWEIA description": request.form["wweia_description"],
            "Energy (kcal)": float(request.form["energy"]) * 100 / scale,
            "Protein (g)": float(request.form["protein"]) * 100 / scale,
            "Carbohydrate (g)": float(request.form["carbo"]) * 100 / scale,
            "Total Sugars (g)": float(request.form["sugar"]) * 100 / scale,
            "Total Fiber (g)": float(request.form["fiber"]) * 100 / scale,
            "Total Fat (g)": float(request.form["fat"]) * 100 / scale,
            "Water (g)": float(request.form["water"]) * 100 / scale,
        }
        food_data.insert_one(new_food)

    return render_template('addfood.html')


@app.post('/<id>/delete/')
@login_required
def delete(id):
    food_data.delete_one({"_id": ObjectId(id)})
    return redirect(url_for('advance'))


if __name__ == "__main__":
    
    # check if password database exists
    if not exists("database.db"):
        with open("database.db", 'w') as fp:
            pass
        with app.app_context():
            passdb.create_all()

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
