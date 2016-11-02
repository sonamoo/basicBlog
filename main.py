import os
import re
from string import letters

import webapp2
import jinja2

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
								autoescape = True)


def render_str(template, **params):
	t = jinja_env.get_template(template)
	return t.render(params)

class Handler(webapp2.RequestHandler):
	def write(self, *a, **kw):
		self.response.out.write(*a, **kw)

	def render_str(self, template, **params):
		return render_str(template, **params)

	def render(self, template, **kw):
		self.write(self.render_str(template, **kw))

# blog_key is for the data store. It stores
def blog_key(name = 'default'):
	return db.Key.from_path('blogs', name) 

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
