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

from models import User

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
  
  
def do_local_logout(request):
  """
  return the user in case you need to do something with it after logout
  """
  if request.session.has_key('user'):
    user = request.session['user']
    
    # don't clear the session
    del request.session['user']
    
    return user
  
  return None

def do_remote_logout(request, user):
  auth_system = AUTH_SYSTEMS[user['type']]
  
  # does the auth system have a special logout procedure?
  if hasattr(auth_system, 'do_logout'):
    response = auth_system.do_logout(request)
    return response

def do_complete_logout(request):
  user = do_local_logout(request)
  if user:
    response = do_remote_logout(request, user)
    return response
  return None
  
def logout(request):
  """
  logout
  """
  response = do_complete_logout(request)
  if response:
    return response
  
  return HttpResponseRedirect(request.GET.get('return_url',"/"))
  
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
  if not request.session.has_key('auth_system_name'):
    do_local_logout(request)
    return HttpResponseRedirect("/")
    
  system = AUTH_SYSTEMS[request.session['auth_system_name']]
  
  # get the user info
  user = system.get_user_info_after_auth(request)

  if user:
    # get the user and store any new data about him
    user_obj = User.update_or_create(user['type'], user['user_id'], user['name'], user['info'], user['token'])
    
    request.session['user'] = user
  else:
    # we were logging out
    pass
  
  return HttpResponseRedirect(request.session['auth_return_url'] or "/")

