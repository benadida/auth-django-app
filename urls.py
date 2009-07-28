"""
Helios Twitter URLs

Ben Adida (ben@adida.net)
"""

from django.conf.urls.defaults import *

from views import *
from auth_systems.password import password_login_view

urlpatterns = patterns('',
    # basic static stuff
    (r'^$', index),
    (r'^logout$', logout),
    (r'^start/(?P<system_name>.*)$', start),
    (r'^after$', after),
    
    # password auth
    (r'^password/login', password_login_view),
)
