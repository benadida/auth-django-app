"""
Facebook Authentication
"""

import logging

from django.conf import settings
APP_ID = settings.FACEBOOK_APP_ID
API_KEY = settings.FACEBOOK_API_KEY
API_SECRET = settings.FACEBOOK_API_SECRET
  
#from facebookclient import Facebook
import urllib, urllib2, cgi

# some parameters to indicate that status updating is possible
STATUS_UPDATES = True
STATUS_UPDATE_WORDING_TEMPLATE = "Send %s to my facebook status"

# FIXME: move this utils somewhere global, not in Helios
from helios import utils

def facebook_url(url, params):
  return "https://graph.facebook.com%s?%s" % (url, urllib.urlencode(params))

def facebook_get(url, params):
  full_url = facebook_url(url,params)
  return urllib2.urlopen(full_url).read()

def _get_new_client(session_key=None):
  fb = Facebook(API_KEY, API_SECRET)
  if session_key:
    fb.session_key = session_key
  return fb

def get_auth_url(request, redirect_url):
  request.session['fb_redirect_uri'] = redirect_url
  return facebook_url('/oauth/authorize', {
      'client_id': APP_ID,
      'redirect_uri': redirect_url,
      'scope': 'publish_stream'})
    
def get_user_info_after_auth(request):
  args = facebook_get('/oauth/access_token', {
      'client_id' : APP_ID,
      'redirect_uri' : request.session['fb_redirect_uri'],
      'client_secret' : API_SECRET,
      'code' : request.GET['code']
      })

  access_token = cgi.parse_qs(args)['access_token'][0]

  import pdb; pdb.set_trace()
  info = utils.from_json(facebook_get('/me', {'access_token':access_token}))

  return {'type': 'facebook', 'user_id' : info['id'], 'name': info['name'], 'info': info, 'token': {'access_token': access_token}}
    
def update_status(user_id, user_info, token, message):
  """
  post a message to the auth system's update stream, e.g. twitter stream
  """
  result = facebook_get('/me/feed', {
      'access_token': token['access_token'],
      'message': message
      })

def send_message(user_id, user_info, subject, body):
  pass
