from google.appengine.ext import db, ndb

class Wish(db.Model):
    #id = db.StringProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)
    updated = db.DateTimeProperty(auto_now=True)
    name = db.StringProperty(required=True)
    details = db.StringProperty(required=True)
    type_of_request = db.StringProperty()
    location_dependent = db.BooleanProperty()
    location = db.StringProperty()
    status = db.StringProperty()  # can be 'requested', 'in progress', 'completed', 'confirmed'
    user_key = db.StringProperty()

