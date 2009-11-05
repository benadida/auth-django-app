"""
Views for authentication

Ben Adida
2009-07-05
"""

from django.http import *
from django.core.urlresolvers import reverse

from view_utils import *

from auth_systems import AUTH_SYSTEMS
import auth

def index(request):
  """
  the page from which one chooses how to log in.
  """
  
  user = get_user(request)

  # single auth system?
  if len(auth.ENABLED_AUTH_SYSTEMS) == 1 and not user:
    return HttpResponseRedirect(reverse(start, args=[auth.ENABLED_AUTH_SYSTEMS[0]])+ '?return_url=' + request.GET.get('return_url', ''))

  if auth.DEFAULT_AUTH_SYSTEM and not user:
    return HttpResponseRedirect(reverse(start, args=[auth.DEFAULT_AUTH_SYSTEM])+ '?return_url=' + request.GET.get('return_url', ''))
    
  return render_template(request,'index', {'return_url' : request.GET.get('return_url', None), 'auth_systems' : auth.ENABLED_AUTH_SYSTEMS})
  
def logout(request):
  """
  logout
  """

  user = request.session['user']
  
  # don't clear the session
  del request.session['user']

  # if there was a user logged in, do some cleanup
  if user:
    auth_system = AUTH_SYSTEMS[user['type']]
    
    # does the auth system have a special logout procedure?
    if hasattr(auth_system, 'do_logout'):
      response = auth_system.do_logout(request)
      if response:
        return response
  
  return HttpResponseRedirect(request.GET.get('return_url',reverse(index)))
  
def start(request, system_name):
  if not (system_name in auth.ENABLED_AUTH_SYSTEMS):
    return HttpResponseRedirect(reverse(index))
    
  request.session.save()
  
  # store in the session the name of the system used for auth
  request.session['auth_system_name'] = system_name
  
  # where to return to when done
  request.session['auth_return_url'] = request.GET.get('return_url', '/')

  # get the system
  system = AUTH_SYSTEMS[system_name]  
  
  # where to send the user to?
  auth_url = system.get_auth_url(request)
  
  if auth_url:
    return HttpResponseRedirect(auth_url)
  else:
    return HttpResponse("an error occurred trying to contact " + system_name +", try again later")

def after(request):
  # which auth system were we using?
  system = AUTH_SYSTEMS[request.session['auth_system_name']]
  
  # get the user info
  user = system.get_user_info_after_auth(request)

  if user:
    request.session['user'] = user
  
  return HttpResponseRedirect(request.session['auth_return_url'] or "/")
  
