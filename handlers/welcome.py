from handlers.handler import Handler

#### Welcome page. After a user logs in.
class Welcome(Handler):
	def get(self):
		if self.user:
			self.render('welcome.html', username = self.user.name)
		else:
			self.redirect('/blog/register')