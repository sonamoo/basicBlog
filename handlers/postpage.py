from google.appengine.ext import db
from handlers.handler import Handler
from models.Article import Article
from models.Comment import Comment
from helpers import *

#### Single article - shows the article that has the id in URL
class PostPage(Handler):
	def get(self, post_id):
		a = Article.check_if_valid_post(post_id)
		if a :
			comments = db.GqlQuery("select * from Comment where post_id = " 
								+ post_id + " order by created desc")
		else :
			self.error(404)
			return

		self.render("permalink.html", a = a, comments = comments)

	#### Handle comments
	def post(self, post_id):
		a = Article.check_if_valid_post(post_id)
		if a :
			if self.user:
				key = db.Key.from_path('Article', int(post_id), parent=blog_key())
				a = db.get(key)
				comment = self.request.get('comment')
				created_by = self.user.name	

				if comment:
					c = Comment(parent = blog_key(), comment = comment, 
								post_id = int(post_id), created_by = created_by)
					c.put()

					comments = db.GqlQuery("select * from Comment where post_id = " 
										+ post_id + " order by created desc")
					self.render("permalink.html", a = a, comments = comments)
			else:
				self.redirect('/blog/login')
		else : 
			self.error(404)
			return 