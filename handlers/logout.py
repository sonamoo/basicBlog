from handlers.handler import Handler

#### Handles log out. Deletes the cookie.
class Logout(Handler):
	def get(self):
		self.logout()
		self.redirect('/blog/')