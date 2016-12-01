import webapp2
from google.appengine.ext import db
from helpers import *

#### Models
from models.User import User
from models.Article import Article
from models.Comment import Comment


#### Basic Handler. The basic functions that app needs are in this handler
class Handler(webapp2.RequestHandler):
	def write(self, *a, **kw):
		self.response.out.write(*a, **kw)

	def render_str(self, template, **params):
		params['user'] = self.user
		t = jinja_env.get_template(template)
		return render_str(template, **params)

	def render(self, template, **kw):
		self.write(self.render_str(template, **kw))

	def set_secure_cookie(self, name, val):
		cookie_val = make_secure_val(val)
		self.response.headers.add_header(
			'Set-Cookie',
			'%s=%s; Path=/' % (name, cookie_val))

	def read_secure_cookie(self, name):
		cookie_val = self.request.cookies.get(name)
		return cookie_val and check_secure_val(cookie_val)

	def login(self, user):
		self.set_secure_cookie('user_id' , str(user.key().id()))

	def logout(self):
		self.response.headers.add_header(
			'Set-Cookie',
			'user_id=; Path=/')

	def initialize(self, *a, **kw):
		webapp2.RequestHandler.initialize(self, *a, **kw)
		uid = self.read_secure_cookie('user_id')
		self.user = uid and User.by_id(int(uid))

#### Shows all the articles.
class MainPage(Handler):
	def get(self):
		articles = db.GqlQuery("select * from Article order by created desc")
		#   articles = Article.all().order('-created')
		#   This is google pocedure language, that can be used to get db.
		self.render("main.html", articles = articles, user = self.user)

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

#### Single comment page from the article's id and comment's id
class CommentPage(Handler):
	def get(self, post_id, comment_id):
		c = Comment.check_if_valid_comment(comment_id)
		if c:
			key = db.Key.from_path('Comment', int(comment_id),
										 parent=blog_key())
			c = db.get(key)

			a_key = db.Key.from_path('Article', int(post_id), parent=blog_key())
			a = db.get(key)
			self.render("comment.html", c = c, a = a)
		else :
			self.error(404)
			return

#### Handles posting article.
class NewPost(Handler):
	def get(self):
		if not self.user:
			self.redirect('/blog/login')
		self.render("newpost.html")

	def post(self):
		if self.user:
			title = self.request.get("title")
			contents = self.request.get("contents")
			created_by = self.user.name
			
			if title and contents:
				a = Article(parent = blog_key(), title = title, 
							contents = contents, created_by = created_by)
				a.put()
				self.redirect('/blog/%s' % str(a.key().id()))
			else:
				error = "We need both a title and the blog content"
				self.render("newpost.html", title = title, contents = contents,
							 error = error)
		else:
			error = "Please login or register to write your story!"
			self.render("error.html", error = error)
		


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

#### Edit comments based on article's id and comment's id
class EditComment(Handler):
	def get(self, post_id, comment_id):

		if self.user:
			key = db.Key.from_path('Comment', int(comment_id),
									 parent=blog_key())
			c = db.get(key)

			if c.created_by == self.user.name:
				self.render("edit-comment.html", c = c)
			else:
				error = "Oops, this is not your comment"
				self.render("error.html", error = error)

		else:
			self.redirect("/blog/login")

	def post(self, post_id, comment_id):
		a = Article.check_if_valid_post(post_id)
		if a :
			c = Comment.check_if_user_owns_comment(comment_id, self.user.name)
			if c:
				c.comment = self.request.get('comment')
				c.put()
				self.redirect('/blog/%s' % post_id)
		else :
			error = "Oops, this is not your comment"
			self.render("error.html", error = error)


#### Delete comments based on article's id and comment's id
class DeleteComment(Handler):
	def get(self, post_id, comment_id):
		if self.user:
			c = Comment.check_if_user_owns_comment(comment_id, self.user.name)
			if c:
				c.delete()
				self.redirect('/blog/%s' % post_id)
			else :
				error = "Oops, this is not your comment"
				self.render("error.html", error = error)

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

#### Handles log out. Deletes the cookie.
class Logout(Handler):
	def get(self):
		self.logout()
		self.redirect('/blog/')

#### Welcome page. After a user logs in.
class Welcome(Handler):
	def get(self):
		if self.user:
			self.render('welcome.html', username = self.user.name)
		else:
			self.redirect('/blog/register')


# Route
app = webapp2.WSGIApplication([
    ('/blog/?', MainPage),
    ('/blog/newpost', NewPost),
    ('/blog/editpost/([0-9]+)', EditPost),
    ('/blog/deletepost/([0-9]+)', DeletePost),
    ('/blog/editcomment/([0-9]+)/([0-9]+)', EditComment),
    ('/blog/deletecomment/([0-9]+)/([0-9]+)', DeleteComment),
    ('/blog/like/([0-9]+)', LikeArticle),
    ('/blog/([0-9]+)', PostPage),
    ('/blog/([0-9]+)/([0-9]+)', CommentPage),
    ('/blog/register', Register),
	('/blog/login', Login),
	('/blog/logout', Logout),
	('/blog/welcome', Welcome)
], debug=True)
