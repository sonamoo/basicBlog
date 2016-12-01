import webapp2
from google.appengine.ext import db
from helpers import *

#### Models
from models.User import User
from models.Article import Article
from models.Comment import Comment

#### Handlers

from handlers.handler import Handler
from handlers.mainpage import MainPage
from handlers.postpage import PostPage
from handlers.commentpage import CommentPage
from handlers.newpost import NewPost
from handlers.editpost import EditPost
from handlers.deletepost import DeletePost
from handlers.likearticle import LikeArticle
from handlers.editcomment import EditComment
from handlers.deletecomment import DeleteComment
from handlers.signup import Signup
from handlers.register import Register
from handlers.login import Login
from handlers.logout import Logout	
from handlers.welcome import Welcome


# Route
app = webapp2.WSGIApplication([
    ('/blog/?', MainPage),
    ('/blog/newpost', NewPost),
    ('/blog/editpost/([0-9]+)', EditPost),
    ('/blog/deletepost/([0-9]+)', DeletePost),
    ('/blog/editcomment/([0-9]+)/([0-9]+)', EditComment),
    ('/blog/deletecomment/([0-9]+)/([0-9]+)', DeleteComment),
    ('/blog/like/([0-9]+)', LikeArticle),
    ('/blog/([0-9]+)', PostPage),
    ('/blog/([0-9]+)/([0-9]+)', CommentPage),
    ('/blog/register', Register),
	('/blog/login', Login),
	('/blog/logout', Logout),
	('/blog/welcome', Welcome)
], debug=True)
