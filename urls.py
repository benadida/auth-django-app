"""
Helios Twitter URLs

Ben Adida (ben@adida.net)
"""

from django.conf.urls.defaults import *

from views import *

urlpatterns = patterns('',
    # basic static stuff
    (r'^$', index),
    (r'^logout$', logout),
    (r'^start/(?P<system_name>.*)$', start),
    (r'^after$', after),
)
