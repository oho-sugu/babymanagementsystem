import cgi

from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db

import os
from google.appengine.ext.webapp import template

class BabyEvent(db.Model):
    eventType = db.StringProperty(multiline=False)
    timestamp = db.DateTimeProperty()

class MainPage(webapp.RequestHandler):
    def get(self):
        template_values = {
                }
        path = os.path.join(os.path.dirname(__file__),'template','index.html')
        self.response.out.write(template.render(path, template_values))

class EventSave(webapp.RequestHandler):
    def post(self):
        self.response.out.write('<html><body>test</body></html>')
        self.redirect('/')

class EventHistory(webapp.RequestHandler):
    def get(self):
        self.response.out.write('<html><body>test</body></html>')

class DeleteEvent(webapp.RequestHandler):
    def get(self):
        self.response.out.write('<html><body>test</body></html>')

class EventStatistics(webapp.RequestHandler):
    def get(self):
        self.response.out.write('<html><body>test</body></html>')

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

