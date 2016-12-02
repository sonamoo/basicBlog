from handlers.handler import Handler
from models.User import User
import helpers

#### Handle user sign up. Shows error if the requirements are not fulfilled.
class Signup(Handler):
	def get(self):
		self.render("sign-up.html")

	def post(self):
		have_error = False
		self.username = self.request.get('username')
		self.password = self.request.get('password')
		self.verify = self.request.get('verify')
		self.email = self.request.get('email')

		params = dict(username = self.username,
						email = self.email)

		if not valid_username(self.username):
			params['error_username'] = "That's not a valid username."
			have_error = True

		if not valid_password(self.password):
			params['error_password'] = "That's not a valid password."
			have_error = True

		elif self.password != self.verify:
			params['error_verify'] = "Your passwords didn't match."
			have_error = True

		if not valid_email(self.email):
			params['error_email'] = "That's not a valid email."
			have_error = True

		if have_error:
			self.render('sign-up.html', **params)
		else:
			self.done()

	def done(self, *a, **kw):
		raise NotImplementedError