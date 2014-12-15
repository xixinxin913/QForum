#!/usr/bin/env python
#
# Copyright Xin Wang @2014.
#
import webapp2
import urllib
from google.appengine.ext.webapp import template
from google.appengine.api import users
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.ext import blobstore
import os
import datetime
from google.appengine.ext import db
from google.appengine.api import users
import cgi
from model import QuestionPool
from model import AnswerPool
from model import FollowPool
import time
from google.appengine.api import mail
import re


class MainHandler(webapp2.RequestHandler):
    def get(self):
      user = users.get_current_user()
      path = os.path.join(os.path.dirname(__file__), 'templates/home.html')
      values=self.request.GET.keys()
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
      elif(count<=offset*10):
        q = db.GqlQuery("SELECT * FROM QuestionPool order by created_time DESC").fetch(10,(offset-1)*10)
        ifNext=False
      else:
        q = db.GqlQuery("SELECT * FROM QuestionPool order by created_time DESC").fetch(10,(offset-1)*10)
        ifNext=True
      # check if the user has sign in
      if user:
      	url = users.create_logout_url('/')
      	url_text = 'Sign Out'
      	template_values = {'user': users.get_current_user().email(),
        'url': url,
        'url_text': url_text,
        'name':user.email(),
        'questions':q,
        'offset':offset,
        'ifNext':ifNext}
      	self.response.out.write(template.render(path, template_values))
      else:
      	url = users.create_login_url(self.request.uri)
      	url_text = 'Sign In'
        template_values = {
        'url': url,
        'url_text': url_text,
        'name':"",
        'questions':q,
        'offset':offset,
        'ifNext':ifNext}
      	self.response.out.write(template.render(path, template_values))


class AddQuestionPage(webapp2.RequestHandler):
	def get(self):
		user = users.get_current_user()
		if user:
			url = users.create_logout_url('/')
			url_text = 'Sign Out'
			path = os.path.join(os.path.dirname(__file__), 'templates/question.html')
			template_values = {'user': users.get_current_user().email(),'url': url,'url_text': url_text,'name':user.email()}
			self.response.out.write(template.render(path, template_values))
		else:
			self.response.write("please sign in to create question")

class CreateQuestion(webapp2.RequestHandler):
  def get(self):
    self.error(404)
    return
  def post(self):
    questionContent=self.request.get("content")
    tags=self.request.get("tag").split(";")
    tags=[str(var).strip( ) for var in tags]
    q = QuestionPool(title=self.request.get("title"),
    content=questionContent,
		userId=users.get_current_user().email(),
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
      if (q.userId==user.email()):
        isAuthor=True
      else:
        isAuthor=False
      template_values = {'user': users.get_current_user().email(),
      'url': url,
      'url_text': url_text,
      'name':user.email(),
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
      template_values = {'user': users.get_current_user().email(),
      'url': url,
      'url_text': url_text,
      'name':user.email(),
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
    self.error(404)
    return 1
  def post(self):
    user = users.get_current_user()
    url = users.create_logout_url('/')
    url_text = 'Sign Out'
    questionKey=urllib.unquote(self.request.get("key"))
    edit=self.request.get("edit")
    if edit:
      q = db.get(questionKey)
      template_values = {'user': users.get_current_user().email(),
      'url': url,
      'url_text': url_text,
      'name':user.email(),
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
    #redict to show the new question
    time.sleep(2)
    self.redirect('/showQuestion?key='+questionKey)

class CreateAnswer(webapp2.RequestHandler):
  def post(self):
    a=AnswerPool(questionKey=self.request.get("questionKey"),
      content=self.request.get("answerContent"),
      userId=self.request.get("answerUser"))
    a.put()
    #redict to show the new answer page
    time.sleep(1)
    self.redirect('/showQuestion?key='+a.questionKey)

    q=db.get(self.request.get("questionKey"))
    mail.send_mail(sender="Example.com Support <support@example.com>",
              to=q.userId,
              subject="Your account has been approved",
              body="""
              Dear Albert:

              Your example.com account has been approved.  You can now visit
              http://www.example.com/ and sign in using your Google Account to
              access new features.

              Please let us know if you have any questions.

              The example.com Team
              """)
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
		  template_values = {'user': users.get_current_user().email(),
		  'url': url,
		  'url_text': url_text,
		  'name':user.email(),
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
        questionKey=self.request.GET['key']
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
        questionKey=a.questionKey
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
      #redirect to the updated vote page
      time.sleep(1)
      self.redirect('/showQuestion?key='+questionKey)


class VoteDown(webapp2.RequestHandler):
  def get(self):
      self.response.write("try again")
      t=self.request.GET['type']
      user=self.request.GET['user']
      if (t=="question"):
        q=db.get(self.request.GET['key'])
        questionKey=self.request.GET['key']
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
        questionKey=a.questionKey
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
      #redirect to the updated vote page
      time.sleep(1)
      self.redirect('/showQuestion?key='+questionKey)

class Search(webapp2.RequestHandler):
  def get(self):
      text=self.request.get("text")
      user = users.get_current_user()
      path = os.path.join(os.path.dirname(__file__), 'templates/showSearch.html')
      q=db.GqlQuery("SELECT * FROM QuestionPool")
      questions=[]
      answers=[]
      a=db.GqlQuery("SELECT * FROM AnswerPool")
      for var in q:
        if (re.search(text, var.content,re.IGNORECASE)):
          questions.append(var)
      for var in a:
        if (re.search(text, var.content,re.IGNORECASE)):
          answers.append(var)
      if user:
        url = users.create_logout_url('/')
        url_text = 'Sign Out'
        template_values = {'user': users.get_current_user().email(),
        'url': url,
        'url_text': url_text,
        'name':user.email(),
        'questions':questions,
        'keyWords':text,
        'answers':answers}
        self.response.out.write(template.render(path, template_values))
      else:
        url = users.create_login_url(self.request.uri)
        url_text = 'Sign In'
        template_values = {'url': url,
        'url_text': url_text,
        'name':"",
        'questions':questions,
        'keyWords':text,
        'answers':answers}
        self.response.out.write(template.render(path, template_values))


class UpdataAnswer(webapp2.RequestHandler):
  def post(self):
      answerKey=self.request.get("key")
      a=db.get(answerKey)
      a.content=self.request.get("content")
      a.modified_time=datetime.datetime.now()
      a.put()
      #redirect to the updated answer page
      time.sleep(1)
      self.redirect('/showQuestion?key='+a.questionKey)

class Follow(webapp2.RequestHandler):
  def get(self):
    self.response.write("please sign in")
  def post(self):
    f=FollowPool(question=db.get(self.request.get("key")),
      userId=self.request.get("user"))
    f.put()
    time.sleep(1)
    self.redirect('/showQuestion?key='+self.request.get("key"))

class ShowFollow(webapp2.RequestHandler):
  def get(self):
    user = users.get_current_user()
    f = db.GqlQuery("SELECT * FROM FollowPool where userId= :1" ,user.email())
    path = os.path.join(os.path.dirname(__file__), 'templates/showFollow.html')
    if user:
      url = users.create_logout_url('/')
      url_text = 'Sign Out'
      template_values = {'user': users.get_current_user().email(),
      'url': url,
      'url_text': url_text,
      'name':user.email(),
      'questions':f}
      self.response.out.write(template.render(path, template_values))
    else:
      self.response.write("please sign in")


class UploadImage(blobstore_handlers.BlobstoreUploadHandler,webapp2.RequestHandler):
  def get(self):
    user = users.get_current_user()
    path = os.path.join(os.path.dirname(__file__), 'templates/uploadImage.html')
    upload_url=blobstore.create_upload_url('/uploadImage')
    blob = blobstore.BlobInfo.all()
    if user:
      url = users.create_logout_url('/')
      url_text = 'Sign Out'
      template_values = {'user': users.get_current_user().email(),
      'url': url,
      'url_text': url_text,
      'name':user.email(),
      'blob':blob,
      'upload_url':upload_url}
      self.response.out.write(template.render(path, template_values))
    else:
      self.response.write("please sign in")

  def post(self):
    try:
      upload = self.get_uploads('file')
      time.sleep(1)
      self.redirect('/uploadImage')
    except:
      self.redirect('/upload_failure.html')

class ShowImage(blobstore_handlers.BlobstoreDownloadHandler):
    def get(self, blob_key):
        #blobstore.delete(blob_key)
        if not blobstore.get(blob_key):
            self.error(404)
        else:
            self.send_blob(blobstore.BlobInfo.get(blob_key))


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
    (r'/voteDown.*',VoteDown),
    (r'/search.*',Search),
    (r'/followQuestion.*',Follow),
    (r'/showFollow.*',ShowFollow),
    (r'/uploadImage.*',UploadImage),
    (r'/showImage/([^/]+)/?.*',ShowImage)
], debug=True)

if __name__ == '__main__':
    main()
