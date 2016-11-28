import os
import re
import hashlib
import hmac
import random

from string import letters

import webapp2
import jinja2

from google.appengine.ext import db

secret = 'SWEiosdjfokweqr'

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
								autoescape = True)

def render_str(template, **params):
	t = jinja_env.get_template(template)
	return t.render(params)

def make_secure_val(val):
	secured_value = hmac.new(secret, val).hexdigest()
	return '%s|%s' % (val, secured_value)

def check_secure_val(secure_val):
	val = secure_val.split('|')[0]
	if secure_val == make_secure_val(val):
		return val

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


def make_salt(length = 5):
	return ''.join(random.choice(letters) for x in xrange(length))

def make_pw_hash(name, pw, salt = None):
	if not salt:
		salt = make_salt()
	h = hashlib.sha256(name + pw + salt).hexdigest()
	return '%s,%s' % (salt, h)

def valid_pw(name, pw, h):
	salt = h.split(',')[0]
	return h == make_pw_hash(name, pw, salt)

# blog_key is for the data store.
def blog_key(name = 'default'):
	return db.Key.from_path('blogs', name)

def users_key(group = 'default'):
	return db.Key.from_path('users', group)

class User(db.Model):
	name = db.StringProperty(required = True)
	pw_hash = db.StringProperty(required = True)
	email = db.StringProperty(required = False)

	@classmethod
	def by_id(cls, uid):
		return User.get_by_id(uid, parent = users_key())

	@classmethod
	def by_name(cls, name):
		u = User.all().filter('name =', name).get()
		return u

	@classmethod
	def register(cls, name, pw, email = None):
		pw_hash = make_pw_hash(name, pw)
		return User(parent = users_key(),
					name = name,
					pw_hash = pw_hash,
					email = email)

	@classmethod
	def verify_user(cls, username, pw):
		u = cls.by_name(username)
		if u and valid_pw(username, pw, u.pw_hash):
			return u

class NoUser(Handler):
	name = "NoUser"
	redirect = "/blog/login"


class Article(db.Model):
	title = db.StringProperty(required = True)
	contents = db.TextProperty(required = True)
	created = db.DateTimeProperty(auto_now_add = True)
	created_by = db.StringProperty(required = False)
	last_modified = db.DateTimeProperty(auto_now = True)
	likes = db.StringListProperty()

	def render(self):
		self._render_text = self.contents.replace('\n', '<br>')
		return render_str("article.html", a = self)

class Comment(db.Model):
	created_by = db.StringProperty(required = True)
	comment = db.TextProperty(required = True)
	post_id = db.IntegerProperty(required = True)
	created = db.DateTimeProperty(auto_now_add = True)
	last_modified = db.DateTimeProperty(auto_now = True)
		
	
class MainPage(Handler):
	def get(self):
		articles = db.GqlQuery("select * from Article order by created desc")
		#   articles = Article.all().order('-created')
		#   This is google pocedure language, that can be used to get db.

		if not self.user:
			self.user = NoUser

		self.render("main.html", articles = articles, username = self.user.name)

class PostPage(Handler):
	def get(self, post_id):
		key = db.Key.from_path('Article', int(post_id), parent=blog_key())
		#key find the article from the post_id passed from the url
		article = db.get(key)

		comments = db.GqlQuery("select * from Comment where post_id = " + post_id + " order by created desc")
		

		if not article:
			self.error(404)
			return

		self.render("permalink.html", article = article, comments = comments)

	def post(self, post_id):
		if self.user:
			key = db.Key.from_path('Article', int(post_id), parent=blog_key())
			article = db.get(key)
			comment = self.request.get('comment')
			created_by = self.user.name	

			if comment:
				c = Comment(parent = blog_key(), comment = comment, post_id = int(post_id), created_by = created_by)
				c.put()

				comments = db.GqlQuery("select * from Comment where post_id = " + post_id + " order by created desc")
				self.render("permalink.html", article = article, comments = comments)

		else:
			self.redirect('/blog/login')

class CommentPage(Handler):
	def get(self, post_id, comment_id):
		key = db.Key.from_path('Comment', int(comment_id),
									 parent=blog_key())
		c = db.get(key)
		self.render("comment.html", c = c)

class NewPost(Handler):
	def get(self):
		self.render("newpost.html")

	def post(self):
		title = self.request.get("title")
		contents = self.request.get("contents")
		created_by = self.user.name


		if title and contents:
			a = Article(parent = blog_key(), title = title, contents = contents, created_by = created_by)
			a.put()
			self.redirect('/blog/%s' % str(a.key().id()))

		else:
			error = "We need both a title and the blog content"
			self.render("newpost.html", title = title, contents = contents, error = error)

class EditPost(Handler):
	def get(self, post_id):
		key = db.Key.from_path('Article', int(post_id), parent=blog_key())
		a = db.get(key)
		self.render("edit-post.html", a = a)


	def post(self, post_id):
		key = db.Key.from_path('Article', int(post_id), parent=blog_key())
		a = db.get(key)
		a.title = self.request.get("title")
		a.contents = self.request.get("contents")
		a.put()
		self.redirect('/blog/%s' % post_id)


class DeletePost(Handler):
	def get(self, post_id):
		key = db.Key.from_path('Article', int(post_id), parent=blog_key())
		a = db.get(key)
		a.delete()
		self.redirect('/blog/')

class LikeArticle(Handler):
	def get(self, post_id):
		key = db.Key.from_path('Article', int(post_id), parent=blog_key())
		#key find the article from the post_id passed from the url
		article = db.get(key)
		uid = self.read_secure_cookie('user_id')

		
		if not self.user:
			self.redirect('/blog/register')
		else:
			if article.created_by != self.user.name:
				
				if article.likes and uid in article.likes:
					article.likes.remove(uid)
				else:
					article.likes.append(uid)

				article.put()
				
				#self.redirect('/blog/%s' % str(article.key().id()))
				self.redirect(self.request.referer)

			else:
				error = "you can\'t like your own post"
				self.render("error.html", error = error)

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
		
		if not self.user:
			self.redirect('/blog/login')

		comment = self.request.get('comment')

		if comment:
			key = db.Key.from_path('Comment', int(comment_id),
									 parent=blog_key())
			c = db.get(key)
			c.comment = self.request.get('comment')
			c.put()
			self.redirect('/blog/%s' % post_id)

class DeleteComment(Handler):
	def get(self, post_id, comment_id):
		if self.user:
			key = db.Key.from_path('Comment', int(comment_id),
									 parent=blog_key())
			c = db.get(key)
			if c.created_by == self.user.name:
				c.delete()
				self.redirect('/blog/%s' % post_id)
			else :
				error = "Oops, this is not your comment"
				self.render("error.html", error = error)


USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
def valid_username(username):
	return username and USER_RE.match(username)

PASS_RE = re.compile(r"^.{3,20}$")
def valid_password(password):
	return password and PASS_RE.match(password)

EMAIL_RE  = re.compile(r'^[\S]+@[\S]+\.[\S]+$')
def valid_email(email):
	return not email or EMAIL_RE.match(email)

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

#	def login(self, user):
#		self.set_secure_cookie('user_id' , str(user.key().id()))

class Logout(Handler):
	def get(self):
		self.logout()
		self.redirect('/blog/register')

class Welcome(Handler):
	def get(self):
		if self.user:
			self.render('welcome.html', username = self.user.name)
		else:
			self.redirect('/blog/register')



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
