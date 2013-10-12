import cgi

from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db

import os
from google.appengine.ext.webapp import template

class BabyEvent(db.Model):
    eventType = db.StringProperty(multiline=False)
    timestamp = db.DateTimeProperty()
    memo      = db.StringProperty(multiline=True)
    eventDescription = db.StringProperty(multiline=False)
    value     = db.StringProperty(multiline=False)
    enable    = db.BooleanProperty()

class BasePage(webapp.RequestHandler):
    def write_template(self, template_file, template_values):
        path = os.path.join(os.path.dirname(__file__),'template',template_file)
        self.response.out.write(template.render(path, template_values))

class MainPage(BasePage):
    def get(self):
        template_values = {
                }
        self.write_template('index.html',template_values)

class EventSave(BasePage):
    def post(self):
        self.redirect('/')

class EventHistory(BasePage):
    def get(self):
        template_values = {
                }
        self.write_template('history.html',template_values)

class DeleteEvent(BasePage):
    def get(self):
        self.redirect('/history')

class EventStatistics(BasePage):
    def get(self):
        template_values = {
                }
        self.write_template('stat.html',template_values)

application = webapp.WSGIApplication(
        [('/', MainPage),
         ('/save', EventSave),
         ('/history', EventHistory),
         ('/delete', DeleteEvent),
         ('/stat', EventStatistics)],
        debug = True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()

