from google.appengine.ext import db
from handlers.handler import Handler
from models.Article import Article
from helpers import *

#### Handles posting article.
class NewPost(Handler):
	def get(self):
		if not self.user:
			self.redirect('/blog/login')
		self.render("newpost.html")

	def post(self):
		if self.user:
			title = self.request.get("title")
			contents = self.request.get("contents")
			created_by = self.user.name
			
			if title and contents:
				a = Article(parent = blog_key(), title = title, 
							contents = contents, created_by = created_by)
				a.put()
				self.redirect('/blog/%s' % str(a.key().id()))
			else:
				error = "We need both a title and the blog content"
				self.render("newpost.html", title = title, contents = contents,
							 error = error)
		else:
			error = "Please login or register to write your story!"
			self.render("error.html", error = error)