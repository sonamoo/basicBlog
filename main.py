import webapp2
import jinja2
import os

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
								autoescape = True)

class Handler(webapp2.RequestHandler):
	def write(self, *a, **kw):
		self.response.out.write(*a, **kw)

	def render_str(self, template, **params):
		t = jinja_env.get_template(template)
		return t.render(params)

	def render(self, template, **kw):
		self.write(self.render_str(template, **kw))


class Article(db.Model):
	title = db.StringProperty(required = True)
	contents = db.StringProperty(required = True)
	created = db.DateTimeProperty(auto_now_add = True)

class MainPage(Handler):
	def blog_render(self, title="", contents=""):
		articles = db.GqlQuery("SELECT * FROM Article "
							   "ORDER BY created DESC ")

		self.render("main.html", title = title, contents = contents, articles = articles)

	def get(self):
		self.blog_render()

class NewPost(Handler):
	def get(self):
		self.render("newpost.html")

	def post(self):
		title = self.request.get("title")
		contents = self.request.get("contents")

		if title and contents:
			a = Article(title = title, contents = contents)
			a.put()

			self.redirect("/blog")

		else:
			error = "We need both a title and the blog content"
			self.blog_render(title, contents, error)


app = webapp2.WSGIApplication([
    ('/blog', MainPage),
    ('/blog/newpost', NewPost)
], debug=True)
