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
import datetime
import webapp2
#import jinja2
import OpenTokSDK
import logging
#from django.utils import simplejson
import json

from google.appengine.ext import db
from google.appengine.api import users

class OpenSessionEntry(db.Model):
  session_id = db.StringProperty()

class ChatPool():
  pass

class MainServerHandler(webapp2.RequestHandler):
  def get(self):
    f = open("index.html")
    index_html = f.read()
    self.response.write(index_html)
    #self.response.write("Hello World!!")
  
  def post(self):
      mySessionEntry = db.GqlQuery("SELECT * "
                            "FROM OpenSessionEntry ").get()
                            #"WHERE ANCESTOR IS :1 ")
                            #"ORDER BY rand LIMIT 1").get()
      
      api_key = "22766332" # Replace with your OpenTok API key.
      api_secret = "4a4bbd01958091ac21dc70b091e423ba11e1182b"  # Replace with your OpenTok API secret.
        
      opentok_sdk = OpenTokSDK.OpenTokSDK(api_key, api_secret)
      
      if not mySessionEntry:
        session_properties = {OpenTokSDK.SessionProperties.p2p_preference: "enable"}
        session = opentok_sdk.create_session(None, session_properties)
        
        newSession = OpenSessionEntry(session_id=session.session_id)
        newSession.put()
              
        mytoken = opentok_sdk.generate_token(session.session_id)
        ret_sid = session.session_id
      else:
        logging.info("hi, google app engine dev! go eat shit")
        mytoken = opentok_sdk.generate_token(mySessionEntry.session_id)
        ret_sid = mySessionEntry.session_id
        mySessionEntry.delete()
        #a=db.GqlQuery("SELECT * FROM OpenSessionEntry").fetch(100)
      
      logging.info("Printing session_id")
      #logging.debug(sessions.session_id)

      #logging.debug(mytoken)
      
      self.response.headers['Content-Type'] = 'application/json'
      #self.response.write(json.dumps({"session_id":pass1,"token":pass2}))
      self.response.write(json.dumps({"session_id":ret_sid,"token":mytoken}))
      #self.response.write(json.dumps({"session_id":len(session),"token":type(session).__name__}))
      
class RoomPage(webapp2.RequestHandler):
    def get(self):
        self.response.out.write('''
        <html>
          <body>
            <form method="post">
              <p>Name: <input type="text" name="name" /></p>
              <p>Favorite foods:</p>
              <select name="favorite_foods" multiple size="4">
                <option value="apples">Apples</option>
                <option value="bananas">Bananas</option>
                <option value="carrots">Carrots</option>
                <option value="durians">Durians</option>
              </select>
              <p>Birth year: <input type="text" name="birth_year" /></p>
              <p><input type="submit" /></p>
            </form>
          </body>
        </html>
        ''')

    def post(self):
        name = self.request.get("name")
        favorite_foods = self.request.get_all("favorite_foods")
        birth_year = self.request.get_range("birth_year",
                                            min_value=1900,
                                            max_value=datetime.datetime.utcnow().year,
                                            default=1900)
        
app = webapp2.WSGIApplication([
    ('/', MainServerHandler),
    ('/room',RoomPage)
], debug=True)
