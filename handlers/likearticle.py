from handlers.handler import Handler
from models.Article import Article
from helpers import *


#### Handles 'like' with the id in URL
class LikeArticle(Handler):
	def get(self, post_id):
		a = Article.check_if_valid_post(post_id)
		uid = self.read_secure_cookie('user_id')

		if a :
			if a.created_by == self.user.name:
				error = "you can\'t like your own post"
				self.render('error.html', error = error)
			elif not self.user:
				self.redirect('/blog/login')
			elif a.likes and uid in a.likes:
				a.likes.remove(uid)
				a.put()
				self.redirect(self.request.referer)

			else:
				a.likes.append(uid)
				a.put()
				self.redirect(self.request.referer)