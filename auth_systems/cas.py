"""
CAS (Princeton) Authentication

Some code borrowed from
https://sp.princeton.edu/oit/sdp/CAS/Wiki%20Pages/Python.aspx
"""

# FIXME: move this utils somewhere global, not in Helios
from helios import utils
from django.http import *

import sys, os, cgi, urllib, re

CAS_URL= 'https://fed.princeton.edu/cas/'
CAS_LOGOUT_URL = 'https://fed.princeton.edu/cas/logout?service=%s'

def _get_service_url(request):
  # FIXME current URL
  from auth.views import after
  from django.conf import settings
  from django.core.urlresolvers import reverse
  
  return settings.URL_HOST + reverse(after)
  
def get_auth_url(request):
  return CAS_URL + 'login?service=' + urllib.quote(_get_service_url(request))
    
def get_user_info_after_auth(request):
  ticket = request.GET.get('ticket', None)
  
  # if no ticket, this is a logout
  if not ticket:
    return None

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
    
def do_logout(request):
  """
  Perform logout of CAS by redirecting to the CAS logout URL
  """
  return HttpResponseRedirect(CAS_LOGOUT_URL % _get_service_url(request))
  
def update_status(token, message):
  """
  post a message to the auth system's update stream, e.g. twitter stream
  """
  # FIXME can't notify someone yet
  pass
