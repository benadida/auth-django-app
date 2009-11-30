"""
CAS (Princeton) Authentication

Some code borrowed from
https://sp.princeton.edu/oit/sdp/CAS/Wiki%20Pages/Python.aspx
"""

# FIXME: move this utils somewhere global, not in Helios
from helios import utils
from django.http import *

import sys, os, cgi, urllib, urllib2, re

CAS_EMAIL_DOMAIN = "princeton.edu"
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

def get_user_info(user_id):
  url = 'http://dsml.princeton.edu/'
  headers = {'SOAPAction': "#searchRequest", 'Content-Type': 'text/xml'}
  
  request_body = """<?xml version='1.0' encoding='UTF-8'?> 
  <soap-env:Envelope 
     xmlns:xsd='http://www.w3.org/2001/XMLSchema'
     xmlns:xsi='http://www.w3.org/2001/XMLSchema-instance'
     xmlns:soap-env='http://schemas.xmlsoap.org/soap/envelope/'> 
     <soap-env:Body> 
        <batchRequest xmlns='urn:oasis:names:tc:DSML:2:0:core'
  requestID='searching'>
        <searchRequest 
           dn='o=Princeton University, c=US'
           scope='wholeSubtree'
           derefAliases='neverDerefAliases'
           sizeLimit='200'> 
              <filter>
                   <equalityMatch name='uid'>
                            <value>%s</value>
                    </equalityMatch>
               </filter>
               <attributes>
                       <attribute name="displayName"/>
                       <attribute name="pustatus"/>
               </attributes>
        </searchRequest>
       </batchRequest>
     </soap-env:Body> 
  </soap-env:Envelope>
""" % user_id

  req = urllib2.Request(url, request_body, headers)
  response = urllib2.urlopen(req).read()
  
  # parse the result
  from xml.dom.minidom import parseString
  
  response_doc = parseString(response)
  
  # get the value elements (a bit of a hack but no big deal)
  values = response_doc.getElementsByTagName('value')
  
  return {'name' : values[0].firstChild.wholeText, 'category' : values[1].firstChild.wholeText}
  
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
    
    info = get_user_info(netid)
    if info:
      name = info['name']
    else:
      name = netid
      
    return {'type': 'cas', 'user_id': netid, 'name': name, 'info': info, 'token': None}
  else:
    return None
    
def do_logout(request):
  """
  Perform logout of CAS by redirecting to the CAS logout URL
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
  if "@" in user_id:
    email = user_id
  else:
    email = "%s@%s" % (user_id, CAS_EMAIL_DOMAIN)
    
  if info.has_key('name'):
    name = info["name"]
  else:
    name = email
    
  send_mail(subject, body, settings.SERVER_EMAIL, ["%s <%s>" % (name, email)], fail_silently=False)
  
def check_constraint(constraint, user_info):
  if not user_info.has_key('category'):
    return False
  return constraint['year'] == user_info['category']
