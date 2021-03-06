#!/usr/bin/env python
#
# Copyright Xin Wang @2014.
#
import webapp2
import urllib
from google.appengine.ext.webapp import template
from google.appengine.api import datastore_errors
from google.appengine.ext.db import ReferencePropertyResolveError
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


"""
retrieve all the questionlist in the database
@return redirct to the homepage
"""
class MainHandler(webapp2.RequestHandler):
    def get(self):
      user = users.get_current_user()
      path = os.path.join(os.path.dirname(__file__), 'templates/home.html')
      values=self.request.GET.keys()
      '''
      q=QuestionPool(title="test",content="test")
      q.put()
      '''
      if ("page" not in values):
          offset=1
      else:
          offset=int(self.request.GET['page'])

      if("sort" not in values):
        sort=False
      else:
        sort=True
      ifNext=True
      #self.response.write(sort)
      # check total number of questions
      count=db.GqlQuery("SELECT * FROM QuestionPool").count()
      # if total number of question less than 10
      if(count <=10):
        if(sort):
          q=db.GqlQuery("SELECT * FROM QuestionPool order by vote DESC, created_time DESC")
        else:
          q=db.GqlQuery("SELECT * FROM QuestionPool order by created_time DESC")
        ifNext=False
      # if the last page hosl less than 10 question
      elif(count<=offset*10):
        if(sort):
          q=db.GqlQuery("SELECT * FROM QuestionPool order by vote DESC, created_time DESC").fetch(10,(offset-1)*10)
        else:
          q = db.GqlQuery("SELECT * FROM QuestionPool order by created_time DESC").fetch(10,(offset-1)*10)
        ifNext=False
      else:
        if(sort):
          q=db.GqlQuery("SELECT * FROM QuestionPool ORDER BY vote DESC, created_time DESC").fetch(10,(offset-1)*10)
        else:
          q = db.GqlQuery("SELECT * FROM QuestionPool order by created_time DESC").fetch(10,(offset-1)*10)
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


"""
show the page for creating new question
"""
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


"""
store the new question in the database
@return redirct to the home page
"""
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
    time.sleep(1)
    self.redirect('/')


"""
show the question content
@return redirct to the show question page
"""
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


"""
show all the questions belongs to a tag
@return redirct to the show tag page
"""
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


"""
show the page to edit question
"""
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
      q = db.get(questionKey)
      q.delete()
      time.sleep(1)
      self.response.write("Question has been deleted")
      self.redirect('/')


"""
update the question in the datastore
@return redirct to the question page with updated content
"""
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
    time.sleep(1)
    self.redirect('/showQuestion?key='+questionKey)

"""
show the page to edit answer
"""
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
      a = db.get(answerKey)
      a.delete()
      time.sleep(1)
      self.response.write("answers has been deleted")
      self.redirect('/showQuestion?key='+a.questionKey)
      

"""
add the ansewer in the datastore, and email the question holder about the new question
@return redirct to the question page with updated answer
"""
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
    mail.send_mail(sender="QForum Support <xw805@nyu.edu>",
              to=q.userId,
              subject="New answer has been added",
              body="""
              Dear User:

              Your question receives a new answer.  You can now visit
              http://wxsamy123.appspot.com/ and sign in using your Google Account to
              access the questions.

              Please let us know if you have any questions.

              The QForum Team
              """)
    self.response.write("answer created successfully")


"""
handling vote up to a question
"""
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


"""
handling vote down of a question
"""
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

"""
handling search by content, using regular expression to find string match
@return redirct to reasrch result
"""
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


"""
update the answer in the datastore
@return redirct to the question page with updated answer
"""

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


"""
add a new follow entity in the datastore
"""

class Follow(webapp2.RequestHandler):
  def get(self):
    self.response.write("please sign in")
  def post(self):
    f=FollowPool(question=db.get(self.request.get("key")),
      userId=self.request.get("user"))
    f.put()
    time.sleep(1)
    self.redirect('/showQuestion?key='+self.request.get("key"))


"""
@return redirct to page showing all question user followed
"""

class ShowFollow(webapp2.RequestHandler):
  def get(self):
    user = users.get_current_user()
    f1=[]
    f = db.GqlQuery("SELECT * FROM FollowPool where userId= :1" ,user.email())
    for var in f:
      try:
        obj = var.question
        f1.append(var)
      except ReferencePropertyResolveError:
        var.delete
    path = os.path.join(os.path.dirname(__file__), 'templates/showFollow.html')
    if user:
      url = users.create_logout_url('/')
      url_text = 'Sign Out'
      template_values = {'user': users.get_current_user().email(),
      'url': url,
      'url_text': url_text,
      'name':user.email(),
      'questions':f1}
      self.response.out.write(template.render(path, template_values))
    else:
      self.response.write("please sign in")


"""
upload image in the blobstore
@return redirct to showing image repository
"""

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


"""
show a image by boblstore key
@return redirct to the page showing the image
"""

class ShowImage(blobstore_handlers.BlobstoreDownloadHandler):
    def get(self, blob_key):
        #blobstore.delete(blob_key)
        if not blobstore.get(blob_key):
            self.error(404)
        else:
            self.send_blob(blobstore.BlobInfo.get(blob_key))


"""
output the xml format of the question and all follwing answers 
"""

class RSS(webapp2.RequestHandler):
  def post(self):
    self.response.write("please sign in")
  def post(self):
    questionKey=self.request.get("key")
    path = os.path.join(os.path.dirname(__file__), 'templates/rss.xml')
    host="http://wxsamy123.appsopt.com/showQuestion?key="+self.request.get("key")
    q = db.get(questionKey)
    a = db.GqlQuery("SELECT * FROM AnswerPool WHERE questionKey= :1 order by vote DESC",questionKey)
    # check if the user has logged in
    template_values = {'host': host,
    'question':q,
    'answers':a}
    self.response.headers["Content-Type"] = 'application/rss+xml'
    self.response.out.write(template.render(path, template_values))


def main():
    app.run()


"""
url handing
"""
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
    (r'/showImage/([^/]+)/?.*',ShowImage),
    (r'/RSS.*',RSS),
    (r'/sort.*',MainHandler)
], debug=True)

if __name__ == '__main__':
    main()
