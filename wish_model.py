from google.appengine.ext import db, ndb

class Wish(db.Model):
    #id = db.StringProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)
    updated = db.DateTimeProperty(auto_now=True)
    tagline = db.StringProperty(required=True)
    details = db.TextProperty(required=True)
    type_of_request = db.StringProperty()
    location_dependent = db.BooleanProperty()
    location = db.StringProperty()
    status = db.StringProperty()  # can be 'requested', 'in progress', 'fulfilled'
    user_key = db.StringProperty()
    user_fulfiller_key = db.StringProperty()

    def time(self):
        return self.created.strftime('%b %d, %Y')

