from google.appengine.ext import db
from helpers import *

#### Article model for database including reder function
class Article(db.Model):
	title = db.StringProperty(required = True)
	contents = db.TextProperty(required = True)
	created = db.DateTimeProperty(auto_now_add = True)
	created_by = db.StringProperty(required = False)
	last_modified = db.DateTimeProperty(auto_now = True)
	likes = db.StringListProperty()

	def render(self):
		self._render_text = self.contents.replace('\n', '<br>')
		return render_str("article.html", a = self)

	@classmethod
	def check_if_valid_post(cls, post_id):
		key = db.Key.from_path('Article', int(post_id), parent=blog_key())
		a = db.get(key)
		if a :
			return a

	@classmethod
	def check_if_user_owns_post(cls, post_id, username):
		a = cls.check_if_valid_post(post_id)
		if a and a.created_by == username:
			return a