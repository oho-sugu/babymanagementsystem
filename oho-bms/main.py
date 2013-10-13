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
    value     = db.StringProperty(multiline=False)
    enable    = db.BooleanProperty()

    typeref = {
            'pee'    : 'おしっこ',
            'boo'    : 'うんち',
            'milk'   : '母乳',
            'formula': 'ミルク',
            'split'  : '吐戻',
            'cloth'  : '着替',
            'bath'   : '沐浴',
            'out'    : '外出',
            'other'  : '他',
            }

    def getValueString(self):
        if self.value == '1':
            return '△'
        elif self.value == '2':
            return '◯'
        elif self.value == '3':
            return '◎'
        else:
            return self.value
    
    def getTypeString(self):
        return self.typeref[self.eventType]

class BasePage(webapp.RequestHandler):
    def write_template(self, template_file, template_values):
        path = os.path.join(os.path.dirname(__file__),'template',template_file)
        self.response.out.write(template.render(path, template_values))

class MainPage(BasePage):
    def get(self):
        dt_now = datetime.today() + timedelta(hours=9)

        template_values = {
            'nowdate': dt_now.strftime('%Y-%m-%d'),
            'nowtime': dt_now.strftime('%H:%M'),
                }
        self.write_template('index.html',template_values)

class EventSave(BasePage):
    def post(self):
        etype = self.request.get('type')
        if etype == 'pee' or etype == 'boo' or etype == 'milk' or etype == 'formula':
            event = BabyEvent()
            event.eventType = etype
            event.timestamp = datetime.strptime(self.request.get('date') + ' ' + self.request.get('time'), '%Y-%m-%d %H:%M')
            event.memo = self.request.get('memo')
            event.value = self.request.get('value')
            event.enable = True
            event.put()

        elif etype == 'peeboo':
            event = BabyEvent()
            event.eventType = 'pee'
            event.timestamp = datetime.strptime(self.request.get('date') + ' ' + self.request.get('time'), '%Y-%m-%d %H:%M')
            event.memo = self.request.get('memo')
            event.value = self.request.get('value')
            event.enable = True
            event.put()

            event = BabyEvent()
            event.eventType = 'boo'
            event.timestamp = datetime.strptime(self.request.get('date') + ' ' + self.request.get('time'), '%Y-%m-%d %H:%M')
            event.memo = self.request.get('memo')
            event.value = self.request.get('value2')
            event.enable = True
            event.put()

        elif etype == 'other':
            event = BabyEvent()
            event.eventType = self.request.get('desc')
            event.timestamp = datetime.strptime(self.request.get('date') + ' ' + self.request.get('time'), '%Y-%m-%d %H:%M')
            event.memo = self.request.get('memo')
            event.value = '-'
            event.enable = True
            event.put()

        self.redirect('/')

class EventHistory(BasePage):
    def get(self):
        display_date = self.request.get('date')
        if not display_date:
            dt_now = datetime.today() + timedelta(hours=9)
        else:
            dt_now = datetime.strptime(display_date,'%Y-%m-%d')

        start = dt_now.replace(hour=0,minute=0,second=0)
        end = dt_now.replace(hour=23,minute=59,second=59)
        baby_events = db.GqlQuery("SELECT * FROM BabyEvent WHERE enable = TRUE AND timestamp >= :1 AND timestamp <= :2 ORDER BY timestamp DESC",start,end)

        dt_yes = (dt_now + timedelta(days=-1)).strftime('%Y-%m-%d')
        dt_tom = (dt_now + timedelta(days= 1)).strftime('%Y-%m-%d')
        template_values = {
                'events'   : baby_events,
                'dt_now'   : dt_now,
                'dt_yes'   : dt_yes,
                'dt_tom'   : dt_tom,
                }
        self.write_template('history.html',template_values)

class DeleteEvent(BasePage):
    def get(self):
        key=self.request.get('key')
        event = BabyEvent.get(db.Key(key))

        event.enable = False
        event.put()

        self.redirect('/history')

class EventStatistics(BasePage):
    def get(self):
        template_values = {
                }
        self.write_template('stat.html',template_values)

class TSVOutput(BasePage):
    def get(self):
        display_date = self.request.get('date')
        if not display_date:
            dt_now = datetime.today() + timedelta(hours=9)
        else:
            dt_now = datetime.strptime(display_date,'%Y-%m-%d')

        start = dt_now.replace(hour=0,minute=0,second=0)
        end = dt_now.replace(hour=23,minute=59,second=59)
        baby_events = db.GqlQuery("SELECT * FROM BabyEvent WHERE enable = TRUE AND timestamp >= :1 AND timestamp <= :2 ORDER BY timestamp DESC",start,end)
        self.response.headers['Content-Type'] = 'text/plain; charset=UTF-8'
        self.response.out.write("時刻\tイベント\t評価\t備考\n")
        for event in baby_events:
            self.response.out.write(event.timestamp)
            self.response.out.write("\t")
            self.response.out.write(event.getTypeString())
            self.response.out.write("\t")
            self.response.out.write(event.getValueString())
            self.response.out.write("\t")
            self.response.out.write(event.memo)
            self.response.out.write("\n")

application = webapp.WSGIApplication(
        [('/', MainPage),
         ('/save', EventSave),
         ('/history', EventHistory),
         ('/tsv', TSVOutput),
         ('/delete', DeleteEvent),
         ('/stat', EventStatistics)],
        debug = True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()

