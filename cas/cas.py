import os
import urllib

from google.appengine.api import users
from google.appengine.ext import ndb
from google.appengine.api import memcache
import json
import jinja2
import webapp2

import time

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)


class MainPage(webapp2.RequestHandler):

    def get(self):
      template_values = {}
      template = JINJA_ENVIRONMENT.get_template('index.html')
      self.response.write(template.render(template_values))

SLEEP_TIME = 5
class Go(webapp2.RequestHandler):
  log = ''
  def add_log(self, val):
    self.log += str(time.time()) + ": " + val + ":::"
  def send_log(self):
    self.report_result(self.log)
  def report_result(self, result):
    self.response.write(json.dumps({ 'result': result}))
    
  def post(self):
    message = json.loads(self.request.body)
    action = message['action']
    speed = message['speed']
    key = message['key']
    value = message.get('value')
    
    memcache_client = memcache.Client()
    log = ''
    if action == 'create':
      self.add_log('Called create')
      if not memcache_client.set(key, {'v':value}):
        self.add_log('Failed to create')
        
    elif action == 'delete':
      self.add_log('Called delete')
      self.add_log('Calling gets('+key+')')
      v = memcache_client.gets(key)
      self.add_log('Value: ' + json.dumps(v))
      if speed == 'slow':
        log += 'Sleeping\n'
        time.sleep(SLEEP_TIME)
      self.add_log('Deleting key: ' + key)
      res = memcache_client.delete(key)
      self.add_log('Result: ' + str(res))
    elif action == 'update':
      self.add_log('Called update')
      retry = 0
      while True:
        self.add_log('Calling gets('+key+')')
        v = memcache_client.gets(key)
        self.add_log('Value: ' + json.dumps(v))
        if v == None:
          self.add_log('Value is None, not setting')
          break
        if value == None:
          v = None;
        else:
          v['v'] = value
        if speed == 'slow':
          log += 'Sleeping\n'
          time.sleep(SLEEP_TIME)
        self.add_log('Updated value to be set: ' + json.dumps(v))
        res = memcache_client.cas(key, v)
        self.add_log('Result: ' + str(res))
        if res or retry > 1:
          break
        retry += 1
    else: 
      self.report_result('Unknown action: ' + action)
      return
    
    self.send_log()


application = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/go', Go),
], debug=True)
