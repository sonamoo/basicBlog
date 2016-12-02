from google.appengine.ext import db
from handlers.handler import Handler
from helpers import *

#### Single comment page from the article's id and comment's id
class CommentPage(Handler):
	def get(self, post_id, comment_id):
		c = Comment.check_if_valid_comment(comment_id)
		if c:
			key = db.Key.from_path('Comment', int(comment_id),
										 parent=blog_key())
			c = db.get(key)

			a_key = db.Key.from_path('Article', int(post_id), parent=blog_key())
			a = db.get(key)
			self.render("comment.html", c = c, a = a)
		else :
			self.error(404)
			return