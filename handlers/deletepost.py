from google.appengine.ext import db
from handlers.handler import Handler
from models.Article import Article
import helpers


#### Deletes the article
class DeletePost(Handler):
	def get(self, post_id):
		a = Article.check_if_user_owns_post(post_id, self.user.name)
		if a:
			a.delete()
			self.redirect('/blog/')
		else :
			error = "This is not your article"
			self.render('error.html', error = error)