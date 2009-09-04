"""
CAS (Princeton) Authentication

Some code borrowed from
https://sp.princeton.edu/oit/sdp/CAS/Wiki%20Pages/Python.aspx
"""

# FIXME: move this utils somewhere global, not in Helios
from helios import utils

import sys, os, cgi, urllib, re

CAS_URL= 'https://fed.princeton.edu/cas/'

def _get_service_url(request):
  # FIXME current URL
  return 'http://localhost:8000/auth/cas/after'
  
def get_auth_url(request):
  return CAS_URL + 'login?service=' + urllib.quote(_get_service_url(request))
    
def get_user_info_after_auth(request):
  ticket = request.GET['ticket']

  # fetch the information from the CAS server
  val_url = CAS_URL + "validate" + \
     '?service=' + urllib.quote(_get_service_url(request)) + \
     '&ticket=' + urllib.quote(ticket)
  r = urllib.urlopen(val_url).readlines()   # returns 2 lines

  # success
  if len(r) == 2 and re.match("yes", r[0]) != None:
    netid = r[1].strip()
    
    return {'type': 'cas', 'user_id': netid, 'name': netid, 'info': None, 'token': None}
  else:
    return None

def update_status(token, message):
  """
  post a message to the auth system's update stream, e.g. twitter stream
  """
  # FIXME can't notify someone yet
  pass
