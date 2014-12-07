#!/usr/bin/env python
#
# Copyright Xin Wang @2014.
#
import webapp2
from google.appengine.ext.webapp import template
from google.appengine.api import users
import os
#from model import Question
import datetime
from google.appengine.ext import db
from google.appengine.api import users
import cgi
from model import QuestionPool


class Question(db.Model):
  questionId = db.StringProperty(required=True)
  content = db.StringProperty(required=True)
  created_date = db.DateProperty()
  tag = db.BooleanProperty(indexed=False)
  userId = db.StringProperty()


class MainHandler(webapp2.RequestHandler):
    def get(self):
      user = users.get_current_user()
      path = os.path.join(os.path.dirname(__file__), 'templates/home.html')
      if user:
      	url = users.create_logout_url('/')
      	url_text = 'Sign Out'
      	q = db.GqlQuery("SELECT * FROM QuestionPool")
      	template_values = {'user': users.get_current_user().nickname(),
        'url': url,
        'url_text': url_text,
        'name':user.nickname(),
        'questions':q}
      	self.response.out.write(template.render(path, template_values))
			# q = Question(questionId="q01",
			# content="test on the first question",
			# userId=users.get_current_user().email())
			# q.created_date = datetime.datetime.now().date()
			# q.put()
      else:
      	url = users.create_login_url(self.request.uri)
      	url_text = 'Sign In'
      	template_values = {'url': url,'url_text': url_text}
      	self.response.out.write(template.render(path, template_values))


class AddQuestionPage(webapp2.RequestHandler):
	def get(self):
		user = users.get_current_user()
		if user:
			url = users.create_logout_url('/')
			url_text = 'Sign Out'
			path = os.path.join(os.path.dirname(__file__), 'templates/question.html')
			template_values = {'user': users.get_current_user().nickname(),'url': url,'url_text': url_text,'name':user.nickname()}
			self.response.out.write(template.render(path, template_values))
		else:
			self.response.write("please sign in to create question")
        	#self.response.out.write(template.render(path, template_values))
        	# url = users.create_login_url(self.request.uri)
        	#url_text = 'Sign In'
         	#path = os.path.join(os.path.dirname(__file__), 'templates/home.html')
         	#template_values = {'url': url,'url_text': url_text}

class CreateQuestion(webapp2.RequestHandler):
  def get(self):
    title=self.request.get("title")
    if (title==""):
      self.response.write("not add question")
    else:
      self.response.write("successfully add question")
  def post(self):
    questionContent=self.request.get("content")
    tags=self.request.get("tag").split(";")
    q = QuestionPool(title=self.request.get("title"),
    content=questionContent,
		userId=users.get_current_user().nickname(),
    tag=tags
    )
    q.put()
    self.response.write("successfully")

class ShowQuestion(webapp2.RequestHandler):
  def get(self):
    user = users.get_current_user()
    url = users.create_logout_url('/')
    url_text = 'Sign Out'
    questionKey=self.request.GET['key']
    path = os.path.join(os.path.dirname(__file__), 'templates/showQuestion.html')
    q = db.get(questionKey)
    if q:
      template_values = {'user': users.get_current_user().nickname(),
      'url': url,
      'url_text': url_text,
      'name':user.nickname(),
      'question':q}
      self.response.out.write(template.render(path, template_values))
    else:
      self.response.out.write("no data")

   
app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/addQuestionPage',AddQuestionPage),
    ('/createQuestion',CreateQuestion),
    (r'/showQuestion.*',ShowQuestion)
], debug=True)

def main():
    app.run()

if __name__ == '__main__':
    main()
