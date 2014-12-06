import datetime
from google.appengine.ext import db
from google.appengine.api import users


class QuestionPool(db.Model):
  title=db.StringProperty(required=True)
  content = db.TextProperty(required=True)
  created_time = db.DateTimeProperty(auto_now_add=True)
  tag = db.StringListProperty()
  userId = db.StringProperty()
  vote=db.IntegerProperty(default=0)