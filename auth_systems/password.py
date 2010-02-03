"""
Username/Password Authentication
"""

# FIXME: move this utils somewhere global, not in Helios
from helios import utils

from django.core.urlresolvers import reverse
from django import forms
from django.core.mail import send_mail
from django.conf import settings
from django.http import HttpResponseRedirect

import logging

def create_user(username, password, name = None):
  from auth.models import User
  
  user = User.get_by_type_and_id('password', username)
  if user:
    raise Exception('user exists')
  
  info = {'password' : password, 'name': name}
  user = User.update_or_create(user_type='password', user_id=username, info = info)
  user.save()

class LoginForm(forms.Form):
  username = forms.CharField(max_length=50)
  password = forms.CharField(widget=forms.PasswordInput(), max_length=100)

def password_check(user, password):
  return (user and user.info['password'] == password)
  
# the view for logging in
def password_login_view(request):
  from auth.view_utils import *
  from auth.views import *
  from auth.models import User
  from django.http import *

  error = None
  
  if request.method == "GET":
    form = LoginForm()
  else:
    form = LoginForm(request.POST)

    if form.is_valid():
      user = User.get_by_type_and_id('password', form.cleaned_data['username'])
      if password_check(user, form.cleaned_data['password']):
        request.session['user'] = user
        return HttpResponseRedirect(reverse(after))
      else:
        error = 'Bad Username or Password'
  
  return render_template(request, 'password/login', {'form': form, 'error': error})
    
def password_forgotten_view(request):
  """
  forgotten password view and submit.
  includes return_url
  """
  from auth.view_utils import *
  from auth.models import User

  if request.method == "GET":
    return render_template(request, 'password/forgot', {'return_url': request.GET.get('return_url', '')})
  else:
    username = request.POST['username']
    return_url = request.POST['return_url']
    
    user = User.get_by_type_and_id('password', username)
    
    body = """

This is a password reminder from Helios:

Your username: %s
Your password: %s

--
Helios
""" % (user.user_id, user.info['password'])

    send_mail('password reminder', body, settings.SERVER_EMAIL, ["%s <%s>" % (user.info['name'], user.info['email'])], fail_silently=False)
    
    return HttpResponseRedirect(return_url)
  
def get_auth_url(request):
  return reverse(password_login_view)
    
def get_user_info_after_auth(request):
  user = request.session['user']
  user_info = user.info
  
  return {'type': 'password', 'user_id' : user.user_id, 'name': user.name, 'info': user.info, 'token': None}
    
def update_status(token, message):
  pass
  
def send_message(user_id, user_info, subject, body):
  if user_info.has_key('email'):
    email = user_info['email']
    name = user_info.get('name', email)
    send_mail(subject, body, "%s <%s>" % ("Helios Voting System", settings.SERVER_EMAIL), ["%s <%s>" % (name, email)], fail_silently=False)    