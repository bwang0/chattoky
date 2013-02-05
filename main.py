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
import OpenTokSDK

import logging
import json
from random import randrange

from google.appengine.ext import db
from google.appengine.api import users

class OpenSessionEntry(db.Model):
  session_id = db.StringProperty()
  prev_session_id = db.StringProperty()

class MainServerHandler(webapp2.RequestHandler):
  def get(self):
    f = open("index.html")
    index_html = f.read()
    self.response.write(index_html)
    #self.response.write("Hello World!!")

  def post(self):
    past_session_id = self.request.get("session_id")

#    mySessionEntry = db.GqlQuery("SELECT * FROM OpenSessionEntry").get()
    if past_session_id == "":
      mySessionEntries_k = db.GqlQuery("SELECT * FROM OpenSessionEntry ").fetch(100,keys_only=True)
    else: # when a person who was paired wants the next room
      mySessionEntries_k = db.GqlQuery("SELECT * FROM OpenSessionEntry WHERE prev_session_id != %s" 
        "AND prev_session_id IN (SELECT prev_session_id FROM OpenSessionEntry WHERE prev_session_id != %s)"
          %(past_session_id,"Nothing")).fetch(100,keys_only=True)

    if len(mySessionEntries_k) == 0:
      mySessionEntry = None
    else:
      # Get a random person to pair with you. This random person is mySessionEntry
      rand_i = randrange(len(mySessionEntries_k))
      mySessionEntry = db.get(mySessionEntries_k[rand_i])

    api_key = "22766332"
    api_secret = "4a4bbd01958091ac21dc70b091e423ba11e1182b"
    opentok_sdk = OpenTokSDK.OpenTokSDK(api_key, api_secret)
    
    # Can not be paired with an existing session/room
    if not mySessionEntry:
      session_properties = {OpenTokSDK.SessionProperties.p2p_preference: "enable"}
      session = opentok_sdk.create_session(None, session_properties)
      
      if past_session_id == "":
        past_session_id = "Nothing"
      newSession = OpenSessionEntry(session_id=session.session_id, prev_session_id=past_session_id)
      newSession.put()
      
      mytoken = opentok_sdk.generate_token(session.session_id)
      ret_sid = session.session_id

    # Successfully paired with an existing session/room, then remove said room from available pool
    else:
      mytoken = opentok_sdk.generate_token(mySessionEntry.session_id)
      ret_sid = mySessionEntry.session_id
      mySessionEntry.delete()
    
    self.response.headers['Content-Type'] = 'application/json'
    self.response.write(json.dumps({"session_id":ret_sid,"token":mytoken}))
 
app = webapp2.WSGIApplication([
    ('/', MainServerHandler)
], debug=True)
