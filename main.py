#!/usr/bin/env python
#
# Copyright Xin Wang @2014.
#
import webapp2
import urllib
from google.appengine.ext.webapp import template
from google.appengine.api import users
import os
#from model import Question
import datetime
from google.appengine.ext import db
from google.appengine.api import users
import cgi
from model import QuestionPool


class MainHandler(webapp2.RequestHandler):
    def get(self):
      user = users.get_current_user()
      path = os.path.join(os.path.dirname(__file__), 'templates/home.html')
      if user:
      	url = users.create_logout_url('/')
      	url_text = 'Sign Out'
      	#q = db.GqlQuery("SELECT * FROM QuestionPool")
        q=QuestionPool.all()
        q.order('-created_time')
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
    tags=[str(var) for var in tags]
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
    #test if current user is auther
    if (q.userId==user.nickname()):
      isAuthor=True
    else:
      isAuthor=False
    if q:
      template_values = {'user': users.get_current_user().nickname(),
      'url': url,
      'url_text': url_text,
      'name':user.nickname(),
      'question':q,
      'isAuthor':isAuthor}
      self.response.out.write(template.render(path, template_values))
    else:
      self.response.out.write("no data")

class ShowTags(webapp2.RequestHandler):
  def get(self):
    questionTag=self.request.GET['tags']
    q = db.GqlQuery("SELECT * FROM QuestionPool where tag= :1" ,questionTag)
    self.response.out.write(q)
    user = users.get_current_user()
    path = os.path.join(os.path.dirname(__file__), 'templates/showTags.html')
    if user:
      url = users.create_logout_url('/')
      url_text = 'Sign Out'
      template_values = {'user': users.get_current_user().nickname(),
      'url': url,
      'url_text': url_text,
      'name':user.nickname(),
      'questions':q,
      'tag':questionTag}
      self.response.out.write(template.render(path, template_values))
    else:
      url = users.create_login_url(self.request.uri)
      url_text = 'Sign In'
      template_values = {'url': url,'url_text': url_text}
      self.response.out.write(template.render(path, template_values))

  def post(self):
    tag=self.request.get("tags")

class EditQuestionPage(webapp2.RequestHandler):
  def get(self):
    self.response.out.write("begin edit")
  def post(self):
    user = users.get_current_user()
    url = users.create_logout_url('/')
    url_text = 'Sign Out'
    questionKey=urllib.unquote(self.request.get("key"))
    edit=self.request.get("edit")
    if edit:
      q = db.get(questionKey)
      template_values = {'user': users.get_current_user().nickname(),
      'url': url,
      'url_text': url_text,
      'name':user.nickname(),
      'question':q}
      path = os.path.join(os.path.dirname(__file__), 'templates/editQuestion.html')
      self.response.out.write(template.render(path, template_values))
    else:
      self.response.out.write("please delete the instance")

class UpdateQuestion(webapp2.RequestHandler):
  def get(self):
    self.response.out.write("over")
  def post(self):
    questionKey=self.request.get("key")
    q=db.get(questionKey)
    tags=self.request.get("tag").split(";")
    tags=[str(var).strip(" ") for var in tags]
    q.content=self.request.get("content")
    q.title=self.request.get("title")
    q.modified_time=datetime.datetime.now()
    q.tag=tags
    q.put()
    self.response.write("rewrite successfully")



app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/addQuestionPage',AddQuestionPage),
    ('/createQuestion',CreateQuestion),
    (r'/showQuestion.*',ShowQuestion),
    (r'/showTags.*',ShowTags),
    (r'/editQuestion.*',EditQuestionPage),
    (r'/updateQuestion.*',UpdateQuestion)
], debug=True)

def main():
    app.run()

if __name__ == '__main__':
    main()
