from handlers.handler import Handler
from handlers.signup import Signup
from models.User import User
import helpers

#### Registers user.
class Register(Signup):
	def done(self):
		u = User.by_name(self.username)
		if u:
			msg = "That user already exists."
			self.render('sign-up.html', error_username = msg)
		else:
			u = User.register(self.username, self.password, self.email)
			u.put()

			self.login(u)
			self.redirect('/blog/welcome')