import datetime
from google.appengine.ext import db
from google.appengine.api import users


class Question(db.Model):
  questionId = db.StringProperty(required=True)
  content = db.StringProperty(required=True)
  created_date = db.DateProperty()
  tag = db.BooleanProperty(indexed=False)
  userId = db.StringProperty()
