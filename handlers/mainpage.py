from google.appengine.ext import db
from handlers.handler import Handler


#### Shows all the articles on the blog front page.
class MainPage(Handler):
	def get(self):
		articles = db.GqlQuery("select * from Article order by created desc")
		#   articles = Article.all().order('-created')
		#   This is google pocedure language, that can be used to get db.
		self.render("main.html", articles = articles, user = self.user)