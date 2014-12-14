import datetime
from google.appengine.ext import db
from google.appengine.api import users
import re


class QuestionPool(db.Model):
	title=db.StringProperty(required=True)
	content = db.TextProperty(required=True)
	created_time = db.DateTimeProperty(auto_now_add=True)
	tag = db.StringListProperty()
	userId = db.StringProperty()
	vote=db.IntegerProperty(default=0)
	voteup_user=db.StringListProperty()
	votedown_user=db.StringListProperty()
	modified_time=db.DateTimeProperty()
	def showImage(self):
		s=self.content
		b = ' <br/>'.join(s.split('\n'))
		r1= re.compile(r'(https?://(?![^" ]*(?:jpg|png|gif))[^" ]+)')
		b = r1.sub(r'<a href="\1" class="links">\1</a>',b)
		r2 = re.compile(r'(https?://[^" ]+\.(jpg|png|gif))')
		b = r2.sub(r'<br><img src="\1" alter="\1" width="100%" height="100%"><br>',b)
		return b
    #parse the tags for displaying the tags when edit
	def showTag(self):
		t=self.tag
		s=""
		for index,var in enumerate (t):
			if(index==len(t)-1):
				s+=var
			else:
				s+=var+";"
		return s



class AnswerPool(db.Model):
	questionKey=db.StringProperty(required=True)
	content=db.TextProperty(required=True)
	created_time = db.DateTimeProperty(auto_now_add=True)
	userId = db.StringProperty()
	vote=db.IntegerProperty(default=0)
	voteup_user=db.StringListProperty()
	votedown_user=db.StringListProperty()
	modified_time=db.DateTimeProperty()

	def showImage(self):
		s=self.content
		b = ' <br />'.join(s.split('\n'))
		r1= re.compile(r'(https?://(?![^" ]*(?:jpg|png|gif))[^" ]+)')
		b = r1.sub(r'<a href="\1" class="links">\1</a>',b)
		r2 = re.compile(r'(https?://[^" ]+\.(jpg|png|gif))')
		b = r2.sub(r'<br><img src="\1" alter="\1" width="100%" height="100%"><br>',b)
		return b


class FollowPool(db.Model):
	userId=db.StringProperty(required=True)
	question=db.ReferenceProperty(QuestionPool)
