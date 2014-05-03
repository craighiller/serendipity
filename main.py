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
        template_values = {}
        template = jinja_environment.get_template("views/home.html")
        self.response.out.write(template.render(template_values))

class WishHandler(BaseHandler):
    def get(self):
        template_values = {}
        template = jinja_environment.get_template("views/make_a_wish.html")
        self.response.out.write(template.render(template_values))

    def post(self):
        wish = Wish(
            name=self.request.get("name"), 
            details=self.request.get("details"), 
            type_of_request=self.request.get("type_of_request"),
            location_dependent=(True if self.request.get("location_dependent") else False),
            location=self.request.get("location")
        )
        wish.put()
        template_values = {}
        template = jinja_environment.get_template("views/make_a_wish_post.html")
        self.response.out.write(template.render(template_values))

class WishIndexHandler(BaseHandler):
    def get(self):
        template_values = {}
        template_values['wishes'] = Wish.all()
        template = jinja_environment.get_template("views/fulfill_a_wish.html")
        self.response.out.write(template.render(template_values))

    def post(self):
        template_values = {}
        template = jinja_environment.get_template("views/fulfill_a_wish_post.html")
        self.response.out.write(template.render(template_values))
        
class LoginHandler(BaseHandler):
    def get(self):
        username = self.request.get("username")
        num = texter.num_parse(self.request.get("phonenumber"))
        cur_user = User.get_by_key_name(username)
        if cur_user == None:
            cur_user = User.get_or_insert(username, name=username, phone_number = num)
        if cur_user.phone_number == num:
            # terrible authentication hacks, sorry Wagner
            self.session['user_name'] = username
            self.session['num'] = num
            self.session['authenticated'] = True
            self.response.out.write("hello world")
            
        else:
            self.session['authenticated'] = False
            self.response.out.write("NOT AUTHENTICATED")
        
            
        
app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/make_a_wish', WishHandler),
    ('/fulfill_a_wish', WishIndexHandler),
    ('/login', LoginHandler)
], debug=True, config=config)
