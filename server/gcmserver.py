#!/usr/bin/python2.4
#
# Copyright 2015 Google Inc. All Rights Reserved.

""" gcm demo
This module is an experiment in getting gcm to work.
"""

import cgi
import logging
import os
import random
import json
import jinja2
import threading
import urllib
import urllib2
import webapp2
from google.appengine.api import memcache
from google.appengine.api import urlfetch

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

class SendPage(webapp2.RequestHandler):
  def write_response(self, result, params, messages):
    # TODO(tkchin): Clean up response format. For simplicity put everything in
    # params for now.
    params['messages'] = messages
    self.response.write(json.dumps({
      'result': result,
      'params': params
    }))

  def write_room_parameters(self, room_id, client_id, messages, is_initiator):
    params = get_room_parameters(self.request, room_id, client_id, is_initiator)
    self.write_response('SUCCESS', params, messages)

  def post(self):
    message = None
    try:
      message = json.loads(self.request.body)
    except Exception as e:
      self.response.write("BAD REQUEST: " + self.request.body)
      return
    
    if "target" in message and "message" in message:
      target = message["target"]
      contents = message["message"]
      server = "https://android.googleapis.com/gcm/send"
      headers = {
        'Authorization': 'key=AIzaSyCqo1RNv9UzqTXPtKRrU2BaFTNaXS-mTzQ',
        'Content-Type': 'application/json'
      }
      
      data = json.dumps({
        'registration_ids': [target],
        'data' : { 'm': contents }
      })
      
      request = urllib2.Request(server, data, headers)
      
      try:
        self.response.write("Sending request:\n")
        self.response.write("Headers: " + json.dumps(headers) + "\n")
        self.response.write("Data:" + data + "\n")
        response = urllib2.urlopen(request).read()
      except Exception as e:
        self.response.write("ERROR SENDING GCM: " + str(e.code) + ":" + e.reason)
        return
      self.response.write("SUCCESS: ");
      self.response.write(json.loads(response))
      return
      
      return
    else:
      self.response.write("BAD REQUEST MISSING PARAMS: " + self.request.body)  
      return

class MainPage(webapp2.RequestHandler):
  def write_response(self, target_page, params={}):
    template = jinja_environment.get_template(target_page)
    content = template.render(params)
    self.response.out.write(content)
    
  def get(self):
    """Renders index.html."""
    self.write_response('index.html')

app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/send', SendPage)
], debug=True)
