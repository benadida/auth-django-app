"""
Data Objects for user authentication

GAE

Ben Adida
(ben@adida.net)
"""

from django.db.models import permalink, signals
from google.appengine.ext import db

from django.utils import simplejson
import datetime, logging

from google.appengine.api import datastore_types

from auth_systems import AUTH_SYSTEMS

class JSONProperty(db.Property):
  """
  extending gae to store a json property
  """
  
  def __init__(self, cls=None, *args, **kwargs):
    super(JSONProperty, self).__init__(self, *args, **kwargs)
    self.json_class = cls
    
  def get_value_for_datastore(self, model_instance):
      value = super(JSONProperty, self).get_value_for_datastore(model_instance)
      return db.Text(self._deflate(value))
      
  def validate(self, value):
      return self._inflate(value)
      
  def make_value_from_datastore(self, value):
      return self._inflate(value)
      
  def _inflate(self, value):
      if value is None:
          return None
      if isinstance(value, unicode) or isinstance(value, str):
          value = simplejson.loads(value)

          # a class to deserialize from
          if self.json_class and value != None:
            value = self.json_class.fromJSONDict(value)
            
      return value
      
  def _deflate(self, value):
      # a class with a specific serialization approach
      if self.json_class and value != None:
        value = value.toJSONDict()
        
      return simplejson.dumps(value)
      
  data_type = datastore_types.Text
    
class User(db.Model):
  user_type = db.StringProperty(multiline=False)
  user_id = db.StringProperty(multiline=False)
    
  name = db.StringProperty(multiline=False)
  
  # other properties
  info = JSONProperty()
  
  # access token information
  token = JSONProperty()
  
  @classmethod
  def _get_type_and_id(cls, user_type, user_id):
    return "%s:%s" % (user_type, user_id)    
    
  @property
  def type_and_id(self):
    return self._get_type_and_id(self.user_type, self.user_id)
    
  @classmethod
  def get_by_type_and_id(cls, user_type, user_id):
    return cls.get_by_key_name(cls._get_type_and_id(user_type, user_id))
  
  @classmethod
  def get_or_create(cls, user_type, user_id, name=None, info=None, token=None):
    key_name = cls._get_type_and_id(user_type, user_id)
    return cls.get_or_insert(key_name, user_type = user_type, user_id = user_id, name=name, info=info, token=token)
    
  def update_status(self, status):
    if AUTH_SYSTEMS.has_key(self.user_type):
      AUTH_SYSTEMS[self.user_type].update_status(self.token, status)
    
  def __eq__(self, other):
    if other:
      return self.key() == other.key()
    else:
      return False
  