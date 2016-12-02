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
			title = self.request.get("title")
			contents = self.request.get("contents")
			if title and contents:
				a.title = title
				a.contents = contents
				a.put()
				self.redirect('/blog/%s' % post_id)
			else:
				error = "We need both a title and blog content"
				self.render("edit-post.html", a = a,
							 error = error)
		else :
			error = "Sorry, This is not your article."
			self.render('error.html', error = error)