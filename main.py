#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import webapp2
import jinja2
import os
import logging
import texter

from webapp2_extras import sessions


from wish_model import Wish
from user_model import User

from google.appengine.ext import db

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))
config = {}
config['webapp2_extras.sessions'] = {
    'secret_key': 'my-super-secret-key',
}

class BaseHandler(webapp2.RequestHandler):
    def dispatch(self):
        # Get a session store for this request.
        self.session_store = sessions.get_store(request=self.request)

        try:
            # Dispatch the request.
            webapp2.RequestHandler.dispatch(self)
        finally:
            # Save all sessions.
            self.session_store.save_sessions(self.response)

    @webapp2.cached_property
    def session(self):
        # Returns a session using the default cookie key.
        return self.session_store.get_session()


class MainHandler(BaseHandler):
    def get(self):
        template_values = {'session':self.session}
        template = jinja_environment.get_template("views/home.html")
        self.response.out.write(template.render(template_values))

class WishHandler(BaseHandler):
    def get(self):
        template_values = {'session':self.session}
        template = jinja_environment.get_template("views/make_a_wish.html")
        self.response.out.write(template.render(template_values))

    def post(self):
        wish = Wish(
            name=self.request.get("name"), 
            details=self.request.get("details"), 
            type_of_request=self.request.get("type_of_request"),
            location_dependent=(True if self.request.get("location_dependent") else False),
            location=self.request.get("location"),
            status="requested"
        )
        wish.put()
        template_values = {'session':self.session}
        template = jinja_environment.get_template("views/make_a_wish_post.html")
        self.response.out.write(template.render(template_values))

class WishIndexHandler(BaseHandler):
    def get(self):
        template_values = {'session':self.session}
        search = self.request.get("status")
        if not search:
            template_values['wishes'] = Wish.all()
        else:
            template_values['wishes'] = Wish.gql("WHERE status = :1", search)
        template = jinja_environment.get_template("views/fulfill_a_wish.html")
        self.response.out.write(template.render(template_values))

    def post(self):
        wish = Wish.get(self.request.get("key"))
        wish.status = 'in progress'
        wish.put()
        template_values = {'session':self.session}
        template = jinja_environment.get_template("views/fulfill_a_wish_post.html")
        self.response.out.write(template.render(template_values))

class UserIndexHandler(BaseHandler):
    def get(self):
        template_values = {'session':self.session}
        search = self.request.get("status")
        template_values['users'] = User.all()
        template = jinja_environment.get_template("views/users.html")
        self.response.out.write(template.render(template_values))
        
class LoginHandler(BaseHandler):
    def get(self):
        template = jinja_environment.get_template("views/login.html")
        template_values = {"denied": False, 'session':self.session}
        
        self.response.out.write(template.render(template_values))
        
    def post(self):
        username = self.request.get("username")
        password = self.request.get("password")
        cur_user = User.get_by_key_name(username)
        template = jinja_environment.get_template("views/login.html")
        
        if cur_user == None:
            template_values = {"denied": True, 'session':self.session}
            self.response.out.write(template.render(template_values))
            return
        if cur_user.password == password:
            # terrible authentication hacks, sorry Wagner
            self.session['user_name'] = username
            self.session['authenticated'] = True
            self.redirect('/')
            
        else:
            self.session['authenticated'] = False
            template_values = {"denied": True, 'session':self.session}
            self.response.out.write(template.render(template_values))

class SignupHandler(BaseHandler):
    def get(self):
        template = jinja_environment.get_template("views/signup.html")
        template_values = {"denied": False, 'session':self.session}

        self.response.out.write(template.render(template_values))

    def post(self):
        username = self.request.get("username")
        password = self.request.get("password")
        num = texter.num_parse(self.request.get("phonenumber"))
        cur_user = User.get_by_key_name(username)
        template = jinja_environment.get_template("views/login.html")
        if cur_user:
            template_values = {"flash": "Sorry, username already exists.", 'session':self.session}
            self.response.out.write(template.render(template_values))
            return
        cur_user = User.get_or_insert(username, name=username, phone_number = num, password=password)        
            # no authentication hacks, sorry Wagner
        self.session['user_name'] = username
        self.session['authenticated'] = True
        self.redirect('/')

                    
class LogoutHandler(BaseHandler):
    def get(self):
        self.session['authenticated'] = False
        self.redirect('/')

class goodbyeHandler(BaseHandler):
    def get(self):
        for wish in Wish.all():
            wish.delete()
        for wish in User.all():
            wish.delete()   
        self.redirect("/")

        
app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/make_a_wish', WishHandler),
    ('/fulfill_a_wish', WishIndexHandler),
    ('/login', LoginHandler),
    ('/signup', SignupHandler),
    
    ('/logout', LogoutHandler),
    ('/users', UserIndexHandler),
    ('/goodbyeFriends', goodbyeHandler)
], debug=True, config=config)
