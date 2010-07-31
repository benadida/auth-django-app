"""
Windows Live Authentication
"""

from django.http import *
from django.core.mail import send_mail
from django.conf import settings

import sys, os, cgi, urllib, urllib2, re
from xml.etree import ElementTree

from openid import view_helpers

# display tweaks
LOGIN_MESSAGE = "Log in with my Windows Live Account"
OPENID_ENDPOINT = 'live.com'

# FIXME!
TRUST_ROOT = 'http://localhost:8000'
RETURN_TO = 'http://localhost:8000/auth/after'

def get_auth_url(request):
  url = view_helpers.start_openid(request.session, OPENID_ENDPOINT, TRUST_ROOT, RETURN_TO)
  return url

def get_user_info_after_auth(request):
  data = view_helpers.finish_openid(request.session, request.GET, RETURN_TO)

  import pdb;pdb.set_trace()
  return data
    
def do_logout(request):
  """
  logout of Yahoo
  """
  return HttpResponseRedirect(CAS_LOGOUT_URL % _get_service_url(request))
  
def update_status(token, message):
  """
  simple update
  """
  pass

def send_message(user_id, user_info, subject, body):
  """
  send email, for now just to Princeton
  """
  # if the user_id contains an @ sign already
  # send_mail(subject, body, settings.SERVER_EMAIL, ["%s <%s>" % (name, email)], fail_silently=False)
  pass
  
def check_constraint(constraint, user_info):
  """
  for eligibility
  """
  pass
