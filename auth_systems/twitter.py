"""
Twitter Authentication
"""

from oauthclient import client

# FIXME: move this utils somewhere global, not in Helios
from helios import utils

import logging

from django.conf import settings
API_KEY = settings['TWITTER_API_KEY']
API_SECRET = settings['TWITTER_API_SECRET']

def _get_new_client(token=None, token_secret=None):
  if token:
    return client.TwitterOAuthClient(API_KEY, API_SECRET, token, token_secret)
  else:
    return client.TwitterOAuthClient(API_KEY, API_SECRET)

def _get_client_by_token(token):
  return _get_new_client(token['oauth_token'], token['oauth_token_secret'])

def get_auth_url(request):
  client = _get_new_client()
  try:
    tok = client.get_request_token()
  except:
    return None
  
  request.session['request_token'] = tok
  url = client.get_authenticate_url(tok['oauth_token']) 
  return url
    
def get_user_info_after_auth(request):
  tok = request.session['request_token']
  twitter_client = _get_client_by_token(tok)
  access_token = twitter_client.get_access_token()
  request.session['access_token'] = access_token
    
  user_info = utils.from_json(twitter_client.oauth_request('https://twitter.com/account/verify_credentials.json', args={}, method='GET'))
  
  import logging
  logging.debug(user_info)
    
  return {'type': 'twitter', 'user_id' : user_info['screen_name'], 'name': user_info['name'], 'info': user_info, 'token': access_token}
    
def _get_client_by_request(request):
  access_token = request.session['access_token']
  return _get_client_by_token(access_token)
  
def update_status(token, message):
  """
  post a message to the auth system's update stream, e.g. twitter stream
  """
  twitter_client = _get_client_by_token(token)
  result = twitter_client.oauth_request('https://twitter.com/statuses/update.xml', args={'status': message}, method='POST')
