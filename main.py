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
import re

from webapp2_extras import sessions


from wish_model import Wish
from user_model import User

from google.appengine.ext import db

import twilio.twiml

import random

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
        template_values['wish'] = Wish.get(self.request.get("key"))
        template_values['flash'] = self.request.get('flash')
        template = jinja_environment.get_template("views/wish.html")
        self.response.out.write(template.render(template_values))

class MakeAWishHandler(BaseHandler):
    def get(self):
        if not self.session['authenticated']:
            return self.redirect('/login?redirect=true')
        template_values = {'session':self.session}
        template = jinja_environment.get_template("views/make_a_wish.html")
        self.response.out.write(template.render(template_values))

    def post(self):
        money = 0
        if self.request.get("cache_money"):
            money = re.sub('[,$ ]', '', self.request.get("cache_money"))

        wish = Wish(
            tagline=self.request.get("tagline"), 
            details=self.request.get("details"), 
            type_of_request=self.request.get("type_of_request"),
            location=self.request.get("location"),
            status="requested",
            user_key=self.session['user_name'],
            cache_money=float(money)
        )
        wish.put()
        self.redirect('/wish?key=' + str(wish.key()) + '&flash=You made a wish!')

class WishIndexHandler(BaseHandler):
    def get(self):
        template_values = {'session':self.session}
        search = self.request.get("status")
        types = self.request.get_all('type_of_request')
        if not types:
            types = ['food', 'animal', 'chores', 'material things', 'other']
            template_values['types'] = types
        else:
            template_values['types'] = types

        if not search:
            search = 'requested'
        template_values['search'] = search

        if search == 'all':
            template_values['wishes'] = Wish.gql("WHERE type_of_request IN :1", types)
        else:
            template_values['wishes'] = Wish.gql("WHERE status = :1 and type_of_request IN :2", search, types)

        template = jinja_environment.get_template("views/fulfill_a_wish.html")
        self.response.out.write(template.render(template_values))

    def post(self):
        if not self.session['authenticated']:
            return self.redirect('/login?redirect=true')
        template_values = {'session':self.session}
        wish = Wish.get(self.request.get("key"))
        if self.request.get('delete'):
            wish.status = 'requested'
            wish.user_fulfiller_key = None
            flash = 'You are no longer fulfilling ' + wish.tagline
        elif self.request.get('confirm'):
            wish.status = 'fulfilled'
            flash = 'Your wish of ' + wish.tagline + ' has been fulfilled!'
        else:
            wish.status = 'in progress'
            wish.user_fulfiller_key = self.session['user_name']
            flash = 'Fulfilling ' + wish.tagline
        wish.put()
        return self.redirect('/wish?key=' + str(wish.key()) + '&flash=' + flash)

class UserHandler(BaseHandler):
    def get(self):
        template_values = {'session':self.session}
        template_values['user'] = User.gql("WHERE name = :1", self.request.get('id')).fetch(1)[0] # shady, get the user w/ username
        template_values['unfulfilled'] = Wish.gql("WHERE user_key = :1 AND status != 'fulfilled'", self.request.get('id'))
        template_values['fulfilled'] = Wish.gql("WHERE user_key = :1 AND status = 'fulfilled'", self.request.get('id'))
        template_values['to_complete'] = Wish.gql("WHERE user_fulfiller_key = :1 AND status != 'fulfilled'", self.request.get('id'))
        template_values['completed'] = Wish.gql("WHERE user_fulfiller_key = :1 AND status = 'fulfilled'", self.request.get('id'))
        template = jinja_environment.get_template("views/user.html")
        self.response.out.write(template.render(template_values))

class UserIndexHandler(BaseHandler):
    def get(self):
        template_values = {'session':self.session}
        template_values['users'] = User.all()
        template = jinja_environment.get_template("views/users.html")
        self.response.out.write(template.render(template_values))
        
class LoginHandler(BaseHandler):
    def get(self):
        template = jinja_environment.get_template("views/login.html")
        template_values = {"denied": False, 'session':self.session}
        if self.request.get('redirect'):
            template_values["denied"] = True
        
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
            self.session['num'] = cur_user.phone_number
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
        opt_in = self.request.get("receive_text")
        num = texter.num_parse(self.request.get("phonenumber"))
        cur_user = User.get_by_key_name(username)
        template = jinja_environment.get_template("views/signup.html")
        if cur_user:
            template_values = {'session':self.session}
            self.response.out.write(template.render(template_values))
            return
        cur_user = User.get_or_insert(username, name=username, phone_number = num, password=password, text_opt_in = opt_in)        
            # no authentication hacks, sorry Wagner
        self.session['user_name'] = username
        self.session['num'] = num
        self.session['authenticated'] = True
        self.redirect('/')

                    
class LogoutHandler(BaseHandler):
    def get(self):
        self.session['user_name'] = ""
        self.session['num'] = ""
        self.session['authenticated'] = False
        self.redirect('/')

class ProfileHandler(BaseHandler):
    def get(self):
        template_values = {'session':self.session}
        template = jinja_environment.get_template("views/profile.html")
        self.response.out.write(template.render(template_values))

class goodbyeHandler(BaseHandler):
    def get(self):
        for wish in Wish.all():
            wish.delete()
        for wish in User.all():
            wish.delete()   
        self.redirect("/")

class twimlHandler(BaseHandler):
    # Will work when called in production, sample request is:
    
    """
    /twiml?ToCountry=US&ToState=NJ&SmsMessageSid=SM3fec99a49092c1f42acc022222e0d288&NumMedia=0&ToCity=RED+BANK&FromZip=07748&SmsSid=SM3fec99a49092c1f42acc022222e0d288&FromState=NJ&SmsStatus=received&FromCity=MIDDLETOWN&Body=Hi&FromCountry=US&To=%2B17329454001&ToZip=08830&MessageSid=SM3fec99a49092c1f42acc022222e0d288&AccountSid=AC16b8cb7d55a29a0425c18637b3398b71&From=%2B17325333935&ApiVersion=2010-04-01
    
    """
    def get(self):
        body = self.request.get("Body")
        from_num = texter.num_parse(self.request.get("From"))
        
        # If you want to insta send back a message, but I think this is useless
        
        #resp = twilio.twiml.Response()
        #resp.message("thank you come again")
        #self.response.out.write(str(resp))

class goodmorningHandler(BaseHandler):
    def get(self):
        for user in User.all():
            if user.text_opt_in:
                self.response.out.write("<b>"+user.name+"</b></br>")
                # Take three random wishes that are not from the user
                user_wishes = random.sample([wish for wish in Wish.all() if wish.user_key != user.name], 3)
                for wish in user_wishes:
                    self.response.out.write(wish.details+"<br>")
            
            
app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/wish', WishHandler),
    ('/make_a_wish', MakeAWishHandler),
    ('/fulfill_a_wish', WishIndexHandler),
    ('/login', LoginHandler),
    ('/signup', SignupHandler),
    ('/logout', LogoutHandler),
    ('/users', UserIndexHandler),
    ('/user', UserHandler),
    ('/profile', ProfileHandler),
    ('/twiml', twimlHandler),
    ('/goodmorning', goodmorningHandler),
    ('/goodbyeFriends', goodbyeHandler)
], debug=True, config=config)
