from google.appengine.ext import db, ndb

class User(db.Model):
    name = db.StringProperty(required=True)
    phone_number = db.StringProperty(required=True)
    password = db.StringProperty(required=True)