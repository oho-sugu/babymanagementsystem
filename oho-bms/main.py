import cgi

from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db

import os
from google.appengine.ext.webapp import template
from datetime import datetime, timedelta

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
        dt_now = datetime.today() + timedelta(hours=9)

        template_values = {
            'nowdate': dt_now.strftime('%Y-%m-%d'),
            'nowtime': dt_now.strftime('%H:%M:%S'),
                }
        self.write_template('index.html',template_values)

class EventSave(BasePage):
    def post(self):
        etype = self.request.get('type')
        if etype == 'pee':
            event = BabyEvent()
            event.eventType = etype
            event.timestamp = datetime.strptime(self.request.get('date') + ' ' + self.requet.get('time'), '%Y-%m-%d %H:%M:%S')
            event.memo = self.requst.get('memo')
            event.eventDescription = ''
            event.value = self.request.get('value')
            event.enable = True
            event.put()

        elif etype == 'boo':
            event = BabyEvent()
            event.eventType = etype
            event.timestamp = datetime.strptime(self.request.get('date') + ' ' + self.requet.get('time'), '%Y-%m-%d %H:%M:%S')
            event.memo = self.requst.get('memo')
            event.eventDescription = ''
            event.value = self.request.get('value')
            event.enable = True
            event.put()

        elif etype == 'peeboo':
            event = BabyEvent()
            event.eventType = 'pee'
            event.timestamp = datetime.strptime(self.request.get('date') + ' ' + self.requet.get('time'), '%Y-%m-%d %H:%M:%S')
            event.memo = self.requst.get('memo')
            event.eventDescription = ''
            event.value = self.request.get('value')
            event.enable = True
            event.put()

            event = BabyEvent()
            event.eventType = 'boo'
            event.timestamp = datetime.strptime(self.request.get('date') + ' ' + self.requet.get('time'), '%Y-%m-%d %H:%M:%S')
            event.memo = self.requst.get('memo')
            event.eventDescription = ''
            event.value = self.request.get('value2')
            event.enable = True
            event.put()

        elif etype == 'milk':
            event = BabyEvent()
            event.eventType = etype
            event.timestamp = datetime.strptime(self.request.get('date') + ' ' + self.requet.get('time'), '%Y-%m-%d %H:%M:%S')
            event.memo = self.requst.get('memo')
            event.eventDescription = ''
            event.value = self.request.get('value')
            event.enable = True
            event.put()

        elif etype == 'formula':
            event = BabyEvent()
            event.eventType = etype
            event.timestamp = datetime.strptime(self.request.get('date') + ' ' + self.requet.get('time'), '%Y-%m-%d %H:%M:%S')
            event.memo = self.requst.get('memo')
            event.eventDescription = ''
            event.value = self.request.get('value')
            event.enable = True
            event.put()

        elif etype == 'other':
            event = BabyEvent()
            event.eventType = etype
            event.timestamp = datetime.strptime(self.request.get('date') + ' ' + self.requet.get('time'), '%Y-%m-%d %H:%M:%S')
            event.memo = self.requst.get('memo')
            event.eventDescription = self.request.get('desc')
            event.value = '0'
            event.enable = True
            event.put()

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

