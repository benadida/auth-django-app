"""
Facebook Authentication
"""

import logging

from django.conf import settings
API_KEY = settings.FACEBOOK_API_KEY
API_SECRET = settings.FACEBOOK_API_SECRET
  
from facebookclient import Facebook

# some parameters to indicate that status updating is possible
STATUS_UPDATES = True
STATUS_UPDATE_WORDING_TEMPLATE = "Send %s to my facebook status"

# FIXME: move this utils somewhere global, not in Helios
from helios import utils

def _get_new_client(session_key=None):
  fb = Facebook(API_KEY, API_SECRET)
  if session_key:
    fb.session_key = session_key
  return fb

def get_auth_url(request):
  client = _get_new_client()
  return client.get_login_url(canvas=False)
    
def get_user_info_after_auth(request):
  client = _get_new_client()
  client.auth_token = request.GET['auth_token']
  client.auth.getSession()

  token = client.session_key
  uid = client.uid
  info = client.users.getInfo([uid], ['name'])

  import logging
  logging.debug(info)
    
  return {'type': 'facebook', 'user_id' : str(uid), 'name': info[0]['name'], 'info': {}, 'token': {'token': token}}
    
def update_status(token, message):
  """
  post a message to the auth system's update stream, e.g. twitter stream
  """
  client = _get_new_client(session_key=token)
  ## FIXME: do the message
  
def send_message(user_id, user_info, subject, body):
  # FIXME: do we DM here?
  pass
