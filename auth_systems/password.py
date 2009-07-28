"""
Username/Password Authentication
"""

# FIXME: move this utils somewhere global, not in Helios
from helios import utils

from django.core.urlresolvers import reverse
from django import forms

def create_user(username, password, name = None):
  from auth.models import User
  
  user = User.get_by_type_and_id('password', username)
  if user:
    raise Exception('user exists')
  
  info = {'password' : password, 'name': name}
  user = User.get_or_create(user_type='password', user_id=username, info = info)
  user.save()

class LoginForm(forms.Form):
  username = forms.CharField(max_length=50)
  password = forms.CharField(widget=forms.PasswordInput(), max_length=100)

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
      if user and user.info['password'] == form.cleaned_data['password']:
        request.session['user'] = user
        return HttpResponseRedirect(reverse(after))
      else:
        error = 'Bad Username or Password'
  
  return render_template(request, 'password/login', {'form': form, 'error': error})
    
  
def get_auth_url(request):
  return reverse(password_login_view)
    
def get_user_info_after_auth(request):
  user = request.session['user']
  user_info = user.info
  
  return {'type': 'password', 'user_id' : user.user_id, 'name': user.name, 'info': user.info, 'token': None}
    
def update_status(token, message):
  pass