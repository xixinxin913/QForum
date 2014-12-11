#!/usr/bin/env python
#
# Copyright Xin Wang @2014.
#
import webapp2
import urllib
from google.appengine.ext.webapp import template
from google.appengine.api import users
import os
import datetime
from google.appengine.ext import db
from google.appengine.api import users
import cgi
from model import QuestionPool
from model import AnswerPool
import time


class MainHandler(webapp2.RequestHandler):
    def get(self):
      user = users.get_current_user()
      path = os.path.join(os.path.dirname(__file__), 'templates/home.html')
      values=self.request.GET.keys()
      # check if the user has sign in
      if user:
      	url = users.create_logout_url('/')
      	url_text = 'Sign Out'
        if ("page" not in values):
          offset=1
        else:
          offset=int(self.request.GET['page'])
        # check total number of questions
        count=db.GqlQuery("SELECT * FROM QuestionPool order by created_time DESC").count()
        # if total number of question less than 10
        if(count <=10):
          q=db.QuestionPool.All()
          ifNext=False
        # if the last page hosl less than 10 question
        elif(count<offset*10):
          q = db.GqlQuery("SELECT * FROM QuestionPool order by created_time DESC").fetch(10,(offset-1)*10)
          ifNext=False
        else:
          q = db.GqlQuery("SELECT * FROM QuestionPool order by created_time DESC").fetch(10,(offset-1)*10)
          ifNext=True
      	template_values = {'user': users.get_current_user().nickname(),
        'url': url,
        'url_text': url_text,
        'name':user.nickname(),
        'questions':q,
        'offset':offset,
        'ifNext':ifNext}
      	self.response.out.write(template.render(path, template_values))
      else:
      	url = users.create_login_url(self.request.uri)
      	url_text = 'Sign In'
        q=QuestionPool.all()
        q.order('-created_time')
        template_values = {
        'url': url,
        'url_text': url_text,
        'name':"",
        'questions':q}
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
    tags=[str(var).strip( ) for var in tags]
    q = QuestionPool(title=self.request.get("title"),
    content=questionContent,
		userId=users.get_current_user().nickname(),
    tag=tags
    )
    q.put()
    self.response.write("successfully")
    time.sleep(2)
    self.redirect('/')

class ShowQuestion(webapp2.RequestHandler):
  def get(self):
    user = users.get_current_user()
    questionKey=self.request.GET['key']
    path = os.path.join(os.path.dirname(__file__), 'templates/showQuestion.html')
    q = db.get(questionKey)
    a = db.GqlQuery("SELECT * FROM AnswerPool WHERE questionKey= :1 order by vote DESC",questionKey)
    # check if the user has logged in
    if user:
      url = users.create_logout_url('/')
      url_text = 'Sign Out'
      if (q.userId==user.nickname()):
        isAuthor=True
      else:
        isAuthor=False
      template_values = {'user': users.get_current_user().nickname(),
      'url': url,
      'url_text': url_text,
      'name':user.nickname(),
      'question':q,
      'isAuthor':isAuthor,
      'answers':a}
      self.response.out.write(template.render(path, template_values))
    else:
      url = users.create_login_url(self.request.uri)
      url_text = 'Sign In'
      template_values = {'url': url,
        'url_text': url_text,
        'name':"",
        'question':q,
        'isAuthor':False,
        'answers':a}
      self.response.out.write(template.render(path, template_values))

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
      template_values = {'url': url,
      'url_text': url_text,
      'name':"",
      'questions':q,
      'tag':questionTag}
      self.response.out.write(template.render(path, template_values))

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

class CreateAnswer(webapp2.RequestHandler):
  def post(self):
    a=AnswerPool(questionKey=self.request.get("questionKey"),
      content=self.request.get("answerContent"),
      userId=self.request.get("answerUser"))
    a.put()
    self.response.write("answer created successfully")

class EditAnswer(webapp2.RequestHandler):
	def post(self):
		answerKey=self.request.get("key")
		a=db.get(answerKey)
		q=db.get(a.questionKey)
		user = users.get_current_user()
		url = users.create_logout_url('/')
		url_text = 'Sign Out'
		questionKey=urllib.unquote(self.request.get("key"))
		edit=self.request.get("edit")
		if edit:
		  template_values = {'user': users.get_current_user().nickname(),
		  'url': url,
		  'url_text': url_text,
		  'name':user.nickname(),
		  'answer':a,
		  'question':q}
		  path = os.path.join(os.path.dirname(__file__), 'templates/editAnswer.html')
		  self.response.out.write(template.render(path, template_values))
		else:
		  self.response.out.write("please delete the instance")

class VoteUp(webapp2.RequestHandler):
  def get(self):
      self.response.write("try again")
      t=self.request.GET['type']
      user=self.request.GET['user']
      if (t=="question"):
        q=db.get(self.request.GET['key'])
        #test if the user has voted for the answer
        #if the user has already vite down for the question
        if (user in q.votedown_user):
          q.votedown_user.remove(user)
          q.voteup_user.append(user)
          q.vote=q.vote+2
        #if user never vote for this question
        elif (user not in q.voteup_user):
          q.voteup_user.append(user)
          q.vote+=1
        q.put()
      else:
        a=db.get(self.request.GET['key'])
        #test if the user has voted for the answer
        #if the user has already vite down for the question
        if (user in a.votedown_user):
          a.votedown_user.remove(user)
          a.voteup_user.append(user)
          a.vote=a.vote+2
        #if user never vote for this question
        elif (user not in a.voteup_user):
          a.voteup_user.append(user)
          a.vote+=1
        a.put()
      self.response.write("vote successfully")




class UpdataAnswer(webapp2.RequestHandler):
	def post(self):
	    answerKey=self.request.get("key")
	    a=db.get(answerKey)
	    a.content=self.request.get("content")
	    a.modified_time=datetime.datetime.now()
	    a.put()
	    self.response.write("rewrite successfully")

class VoteDown(webapp2.RequestHandler):
  def get(self):
      self.response.write("try again")
      t=self.request.GET['type']
      user=self.request.GET['user']
      if (t=="question"):
        q=db.get(self.request.GET['key'])
        #test if the user has voted for the answer
        #if the user has already vite down for the question
        if (user in q.voteup_user):
          q.voteup_user.remove(user)
          q.votedown_user.append(user)
          q.vote=q.vote-2
        #if user never vote for this question
        elif (user not in q.votedown_user):
          q.votedown_user.append(user)
          q.vote-=1
        q.put()
      else:
        a=db.get(self.request.GET['key'])
        #test if the user has voted for the answer
        #if the user has already vite down for the question
        if (user in a.voteup_user):
          a.voteup_user.remove(user)
          a.votedown_user.append(user)
          a.vote=a.vote-2
        #if user never vote for this question
        elif (user not in a.votedown_user):
          a.votedown_user.append(user)
          a.vote-=1
        a.put()
      self.response.write("vote successfully")



def main():
    app.run()

app = webapp2.WSGIApplication([
    ('/', MainHandler),
    (r'/page.*', MainHandler),
    ('/addQuestionPage',AddQuestionPage),
    ('/createQuestion',CreateQuestion),
    (r'/showQuestion.*',ShowQuestion),
    (r'/showTags.*',ShowTags),
    (r'/editQuestion.*',EditQuestionPage),
    (r'/updateQuestion.*',UpdateQuestion),
    (r'/createAnswer.*',CreateAnswer),
    (r'/editAnswer.*',EditAnswer),
    (r'/updateAnswer.*',UpdataAnswer),
    (r'/voteUp.*',VoteUp),
    (r'/voteDown.*',VoteDown)
], debug=True)

if __name__ == '__main__':
    main()
