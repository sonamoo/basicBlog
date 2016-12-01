from handlers.handler import Handler
from models.Article import Article
from helpers import *

#### Handles editing article.
class EditPost(Handler):
	def get(self, post_id):
		a = Article.check_if_user_owns_post(post_id, self.user.name)
		if a:
			self.render("edit-post.html", a = a)
		else :
			error = "Sorry, This is not your article"
			self.render('error.html', error = error)

	def post(self, post_id):
		a = Article.check_if_user_owns_post(post_id, self.user.name)
		if a:
			a.title = self.request.get("title")
			a.contents = self.request.get("contents")
			a.put()
			self.redirect('/blog/%s' % post_id)
		else :
			error = "Sorry, This is not your article."
			self.render('error.html', error = error)