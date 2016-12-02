from google.appengine.ext import db
import helpers

#### Comment model for database
class Comment(db.Model):
	created_by = db.StringProperty(required = True)
	comment = db.TextProperty(required = True)
	post_id = db.IntegerProperty(required = True)
	created = db.DateTimeProperty(auto_now_add = True)
	last_modified = db.DateTimeProperty(auto_now = True)

	@classmethod
	def check_if_valid_comment(cls, comment_id):
		key = db.Key.from_path('Comment', int(comment_id), parent=blog_key())
		c = db.get(key)
		if c :
			return c

	@classmethod
	def check_if_user_owns_comment(cls, comment_id, username):
		c = cls.check_if_valid_comment(comment_id)
		if c and c.created_by == username:
			return c