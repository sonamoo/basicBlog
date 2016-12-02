from handlers.handler import Handler
from models.User import User
import helpers

#### Hnadle user log in
class Login(Handler):
	def get(self):
		self.render('login-form.html')
	def post(self):
		username = self.request.get('username')
		password = self.request.get('password')

		u = User.verify_user(username, password)
		if u:
			self.login(u)
			self.redirect('/blog/welcome')
		else:
			msg = "Invalid login"
			self.render('login-form.html', error = msg)