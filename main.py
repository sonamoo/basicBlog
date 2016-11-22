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

# blog_key is for the data store. It stores
def blog_key(name = 'default'):
	return db.Key.from_path('blogs', name)

def users_key(group = 'default'):
	return db.Key.from_path('users', group)



class Article(db.Model):
	title = db.StringProperty(required = True)
	contents = db.TextProperty(required = True)
	created = db.DateTimeProperty(auto_now_add = True)
	last_modified = db.DateTimeProperty(auto_now = True)

	def render(self):
		self._render_text = self.contents.replace('\n', '<br>')
		return render_str("article.html", a = self)
	
class MainPage(Handler):
	def get(self):
		articles = db.GqlQuery("select * from Article order by created desc limit 10")
		#   articles = Article.all().order('-created')
		#   This is google pocedure language, that can be used to get db.
		self.render("main.html", articles = articles)

class PostPage(Handler):
	def get(self, post_id):
		key = db.Key.from_path('Article', int(post_id), parent=blog_key())
		#key find the article from the post_id passed from the url
		article = db.get(key)

		if not article:
			self.error(404)
			return

		self.render("permalink.html", article = article)

class User(db.Model):
	name = db.StringProperty(required = True)
	pw_hash = db.StringProperty(required = True)
	email = db.StringProperty()

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
	def verify_user(cls, name, pw):
		u = cls.by_name(name)
		if u and valid_pw(name, pw, u.pw_hash):
			return u

			


class NewPost(Handler):
	def get(self):
		self.render("newpost.html")

	def post(self):
		title = self.request.get("title")
		contents = self.request.get("contents")

		if title and contents:
			a = Article(parent = blog_key(), title = title, contents = contents)
			a.put()
			self.redirect('/blog/%s' % str(a.key().id()))

		else:
			error = "We need both a title and the blog content"
			self.render("newpost.html", title = title, contents = contents, error = error)


app = webapp2.WSGIApplication([
    ('/blog/?', MainPage),
    ('/blog/newpost', NewPost),
    ('/blog/([0-9]+)', PostPage)
], debug=True)
