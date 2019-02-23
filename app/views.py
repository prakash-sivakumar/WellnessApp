from app import app, lm
from flask import request, redirect, render_template, url_for, flash, jsonify
from flask.ext.login import login_user, logout_user, login_required, current_user
from .forms import LoginForm
from .user import User
from werkzeug.security import generate_password_hash
import json
from bson import ObjectId
import calendar
from collections import OrderedDict


@app.route('/')
@login_required
def home():
    return render_template('home.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    collection = app.config['USERS_COLLECTION']
    if request.method == 'POST' and form.validate_on_submit():
        user = collection.find_one({"username": form.username.data})
        if user and User.validate_login(user['password'], form.password.data):
            user_obj = User(user['username'])
            login_user(user_obj)
            flash("Logged in successfully!", category='success')
            return redirect(url_for("home"))
        flash("Wrong username or password!", category='error')
    return render_template('login.html', title='login', form=form)

@app.route('/signup', methods= ['GET', 'POST'])
def signup():
    collection = app.config['USERS_COLLECTION']
    form = LoginForm()
    username = form.username.data
    password = form.password.data
    if request.method == 'POST' and form.validate_on_submit():
        pass_hash = generate_password_hash(password, method='pbkdf2:sha256')
        # Insert the user in the DB
        user = collection.find_one({"username": username})
        if user:
            flash("User already exists!", category='error')
        else:
            collection.insert({"username": username, "password": pass_hash})
            flash("Signed up successfully! Login to continue.", category='success')
    return render_template('signup.html', title = 'signup', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/chat', methods=['GET', 'POST'])
@login_required
def chat():
    return render_template('chat.html')

@app.route('/music', methods=['GET', 'POST'])
@login_required
def music():
    return render_template('music.html')



@app.route('/schedules', methods=['GET', 'POST'])
@login_required
def schedules():
    result = OrderedDict()
    collection = app.config['EVENT_COLLECTION']
    days = ["MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY", "SATURDAY", "SUNDAY"]
    months = ["JANUARY", "FEBRUARY", "MARCH", "APRIL", "MAY", "JUNE", "JULY", "AUGUST", "SEPTEMBER", "OCTOBER", "NOVEMBER", "DECEMBER"]
    cursor = collection.find({"user" : current_user.get_id()}).sort("isoDate" , 1)
    listOfObjects = list(cursor)
    for i in listOfObjects:
        i['_id'] = str(i['_id'])
        dateArray = i['date'].split("/")
        dayValue = calendar.weekday(int(dateArray[2]), int(dateArray[0]), int(dateArray[1]))
        i["day"] = days[dayValue]
        monthValue = int(dateArray[0]) - 1
        i["month"] = months[monthValue]
        i["year"] = dateArray[2]
        if i['date'] in result.keys():
            result[i['date']].append(i)
        else:
            result[i['date']] = list()
            result[i['date']].append(i)
    return render_template('schedules.html', data = result)

@app.route('/addSchedule', methods=['GET', 'POST'])
@login_required
def addSchedule():
    return render_template('add_schedule.html')

@app.route('/contactus', methods = ['GET', 'POST'])
@login_required
def contact():
    return render_template('contact.html')

@app.route('/help', methods = ['GET', 'POST'])
@login_required
def help():
    return render_template('help.html')

@app.route('/addContact', methods = ['GET', 'POST'])
@login_required
def addContact():
    if request.method == 'POST':
        jsonValue = request.get_json()
        collection = app.config['FEEDBACK_COLLECTION']
        fname = jsonValue.get('fname')
        lname = jsonValue.get('lname')
        email = jsonValue.get('email')
        subject = jsonValue.get('subject')
        collection.insert({"fname": fname, "lname": lname, "email": email, "subject": subject})
        flash("Feedback submitted!", category='success')
        return "success"


@app.route('/addEvent', methods=['POST'])
@login_required
def addEvent():
    jsonValue = request.get_json()
    collection = app.config['EVENT_COLLECTION']
    eventName = jsonValue.get('eventName')
    date = jsonValue.get('date')
    isoDate = jsonValue.get('isoDate')
    time1 = jsonValue.get('time1')
    time2 = jsonValue.get('time2')
    collection.insert({"event": eventName, "date" : date, "isoDate" : isoDate, "user" : current_user.get_id(), "time1" : time1, "time2" : time2})
    flash("Event added!", category='success')
    return "success"

@app.route('/deleteEvent', methods=['POST'])
@login_required
def deleteEvent():
    jsonValue = request.get_json()
    collection = app.config['EVENT_COLLECTION']
    for id in jsonValue.get("objectIds"):
        oid = ObjectId(id)
        collection.remove({"_id" : oid})
    return redirect(url_for('schedules'))


@app.route('/getEvents', methods=['GET'])
@login_required
def getEvents():
    collection = app.config['EVENT_COLLECTION']
    days = ["MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY", "SATURDAY", "SUNDAY"]
    months = ["JANUARY", "FEBRUARY", "MARCH", "APRIL", "MAY", "JUNE", "JULY", "AUGUST", "SEPTEMBER", "OCTOBER", "NOVEMBER", "DECEMBER"]
    cursor = collection.find({"user" : current_user.get_id()}).sort("isoDate" , 1)
    result = {}
    listOfObjects = list(cursor)
    for i in listOfObjects:
        i['_id'] = str(i['_id'])
        dateArray = i['date'].split("/")
        dayValue = calendar.weekday(int(dateArray[2]), int(dateArray[0]), int(dateArray[1]))
        i["day"] = days[dayValue]
        monthValue = int(dateArray[0]) - 1
        i["month"] = months[monthValue]
        i["year"] = dateArray[2]
        if i['date'] in result.keys():
            result[i['date']].append(i)
        else:
            result[i['date']] = list()
            result[i['date']].append(i)
    return jsonify(result)

@app.route('/exercises', methods=['GET', 'POST'])
@login_required
def exercises():
    collection = app.config['EXERCISE_COLLECTION']
    cursor = collection.find({"user" : current_user.get_id()}).sort("date" , 1)
    result = []
    for i in list(cursor):
        result.append([i['date'], 1])
    print result
    return render_template('exercises.html', data = json.dumps(result))

@app.route('/addExercise', methods=['POST'])
@login_required
def addExercise():
    jsonValue = request.get_json()
    collection = app.config['EXERCISE_COLLECTION']
    exercisetype = jsonValue.get('exercisetype')
    date = jsonValue.get('date')
    collection.insert({"exercise": exercisetype, "date" : date, "user" : current_user.get_id()})
    flash("Exercise added!", category='success')
    return "success"



@lm.user_loader
def load_user(username):
    u = app.config['USERS_COLLECTION'].find_one({"username": username})
    if not u:
        return None
    return User(u['username'])

