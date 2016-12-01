from google.appengine.ext import db
from handlers.handler import Handler
from models.Article import Article
from models.Comment import Comment
from helpers import *


#### Edit comments based on article's id and comment's id
class EditComment(Handler):
	def get(self, post_id, comment_id):

		if self.user:
			key = db.Key.from_path('Comment', int(comment_id),
									 parent=blog_key())
			c = db.get(key)

			if c.created_by == self.user.name:
				self.render("edit-comment.html", c = c)
			else:
				error = "Oops, this is not your comment"
				self.render("error.html", error = error)

		else:
			self.redirect("/blog/login")

	def post(self, post_id, comment_id):
		a = Article.check_if_valid_post(post_id)
		if a :
			c = Comment.check_if_user_owns_comment(comment_id, self.user.name)
			if c:
				c.comment = self.request.get('comment')
				c.put()
				self.redirect('/blog/%s' % post_id)
		else :
			error = "Oops, this is not your comment"
			self.render("error.html", error = error)