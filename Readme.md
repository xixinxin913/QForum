XIN WANG
Open Source Tools
Prof. Jeffrey Korn 
12/16/2014

Final Project-- Question Forum
------------------------------------------------------------------------------------------------
Codes on: https://github.com/xixinxin913/QForum See Demo on http://wxsamy123.appspot.com/
Feeds in Atom standard available on master branch for each question,feeds feature disabled on tag: experiment

Main functionality:
====================
1. for users who don't log in, they can access to following function
   a. view all the question lists
   b. search for question and answer by keywords in content
   c. smart sort the question by vote and time
   d. view detail question content, answer and vote for each question by click on question title

2. For users who have login, they can access to more function except for functions that are same with ....
   a. create questions in the create question page
   b. create answer in the bottom at view question page
   c. vote up and down for the questions and answers, but the system only record the last vote for them
   d. edit the questions and answers created by user
   e. can RSS to each questions, that dumps all questions and answers in XML format
   f. can upload image by on the uploadImage page. once the image is uploaded, it wil show up in the image repository page. every login user can view the image repository, and refer to theses images in the question and answers by the copying url 


Additional function
======================
1.Support a moderator mode where a special user can remove questions or answers: each user can remove the question and answer created by themselves

2.Support emailing updates, where any answer posted will get sent to the person asking the question

3.Allow viewers to search for questions or answers by text in the contents.

4.Allow users the ability to follow a question, and create a view page that shows all of the followed questions.

5. Allow "smarter" sorting of questions, that uses a combination of activity most vote and time to better rank the questions.


Documentation:
======================
The app is written in Python and deployed with App Engine. It is also developed using GIT, with regular code commits, and store data in Google App Engine's data store, render HTML with templates.

1. data model: build up four models. each for questions, answers, follows, and using blobstore to store image

2. html template: using 10 different html template, including editAnswer.html,editQuestion.html,home.html,question.html,rss.xml,showFollow.html,zhowQuestion.html,showSearch.html,showTags.html,uploadImage.html

3. main.py: all functions communicate back and forth between sever, html, and datbase
