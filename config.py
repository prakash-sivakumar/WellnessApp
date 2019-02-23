from pymongo import MongoClient

WTF_CSRF_ENABLED = True
SECRET_KEY = 'Put your secret key here'
DB_NAME = 'assistiveDB'

DATABASE = MongoClient()[DB_NAME]
USERS_COLLECTION = DATABASE.users
EVENT_COLLECTION = DATABASE.events
EXERCISE_COLLECTION = DATABASE.exercises
FEEDBACK_COLLECTION = DATABASE.feedback

DEBUG = True
