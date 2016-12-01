from google.appengine.ext import db
from handlers.handler import Handler
from models.Comment import Comment
from helpers import *

#### Delete comments based on article's id and comment's id
class DeleteComment(Handler):
	def get(self, post_id, comment_id):
		if self.user:
			c = Comment.check_if_user_owns_comment(comment_id, self.user.name)
			if c:
				c.delete()
				self.redirect('/blog/%s' % post_id)
			else :
				error = "Oops, this is not your comment"
				self.render("error.html", error = error)