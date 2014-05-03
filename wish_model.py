from google.appengine.ext import db, ndb

class User(db.Model):
    id = db.StringProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)
    updated = db.DateTimeProperty(auto_now=True)
    name = db.StringProperty(required=True)
    details = db.StringProperty(required=True)
    type_of_request = db.StringProperty()
    location_dependent = db.BooleanProperty()
    location = db.StringProperty()