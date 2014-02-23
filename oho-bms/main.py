import cgi

from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db

import os
from google.appengine.ext.webapp import template
from datetime import datetime, timedelta


class BabyEvent(db.Model):
    eventType = db.StringProperty(multiline=False)
    timestamp = db.DateTimeProperty()
    memo = db.StringProperty(multiline=True)
    value = db.StringProperty(multiline=False)
    enable = db.BooleanProperty()

    typeref = \
        {
            'pee': 'おしっこ',
            'boo': 'うんち',
            'milk': '母乳',
            'formula': 'ミルク',
            'split': '吐戻',
            'cloth': '着替',
            'bath': '沐浴',
            'out': '外出',
            'other': '他',
            'return': '帰宅',
            'onset': '入眠',
            'wake': '起床',
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
        if self.eventType in self.typeref:
            return self.typeref[self.eventType]
        else:
            return ''


class BasePage(webapp.RequestHandler):
    def login(self):
        user = users.get_current_user()

        if user:
            return
        else:
            self.redirect(users.create_login_url(self.request.uri))

    def write_template(self, template_file, template_values):
        path = os.path.join(os.path.dirname(__file__), 'template', template_file)
        self.response.out.write(template.render(path, template_values))


class MainPage(BasePage):
    def get(self):
        dt_now = datetime.today() + timedelta(hours=9)

        template_values = {
            'nowdate': dt_now.strftime('%Y-%m-%d'),
            'nowtime': dt_now.strftime('%H:%M'),
                }
        self.write_template('index.html', template_values)


class EventSave(BasePage):
    def post(self):
        etype = self.request.get('type')
        if etype == 'pee' or etype == 'boo' or etype == 'milk' or etype == 'formula':
            event = BabyEvent()
            event.eventType = etype
            event.timestamp = datetime.strptime(
                self.request.get('date') + ' ' + self.request.get('time'), '%Y-%m-%d %H:%M')
            event.memo = self.request.get('memo')
            event.value = self.request.get('value')
            event.enable = True
            event.put()

        elif etype == 'peeboo':
            event = BabyEvent()
            event.eventType = 'pee'
            event.timestamp = datetime.strptime(
                self.request.get('date') + ' ' + self.request.get('time'), '%Y-%m-%d %H:%M')
            event.memo = self.request.get('memo')
            event.value = self.request.get('value')
            event.enable = True
            event.put()

            event = BabyEvent()
            event.eventType = 'boo'
            event.timestamp = datetime.strptime(
                self.request.get('date') + ' ' + self.request.get('time'), '%Y-%m-%d %H:%M')
            event.memo = self.request.get('memo')
            event.value = self.request.get('value2')
            event.enable = True
            event.put()

        elif etype == 'other':
            event = BabyEvent()
            event.eventType = self.request.get('desc')
            event.timestamp = datetime.strptime(
                self.request.get('date') + ' ' + self.request.get('time'), '%Y-%m-%d %H:%M')
            event.memo = self.request.get('memo')
            event.value = '-'
            event.enable = True
            event.put()

        self.redirect('/history')


class EventHistory(BasePage):
    def get(self):
        display_date = self.request.get('date')
        if not display_date:
            dt_now = datetime.today() + timedelta(hours=9)
        else:
            dt_now = datetime.strptime(display_date,'%Y-%m-%d')

        start = dt_now.replace(hour=0,minute=0,second=0)
        end = dt_now.replace(hour=23,minute=59,second=59)
        baby_events = db.GqlQuery(
            "SELECT * FROM BabyEvent "
            "WHERE enable = TRUE AND timestamp >= :1 AND timestamp <= :2 ORDER BY timestamp DESC",
            start, end)

        dt_yes = (dt_now + timedelta(days=-1)).strftime('%Y-%m-%d')
        dt_tom = (dt_now + timedelta(days= 1)).strftime('%Y-%m-%d')
        template_values =\
            {
                'events': baby_events,
                'dt_now': dt_now,
                'dt_yes': dt_yes,
                'dt_tom': dt_tom,
            }
        self.write_template('history.html', template_values)


class DeleteEvent(BasePage):
    def get(self):
        key = self.request.get('key')
        event = BabyEvent.get(db.Key(key))

        event.enable = False
        event.put()

        self.redirect('/history')


class EventStatistics(BasePage):
    def get(self):
        display_date = self.request.get('date')
        if not display_date:
            dt_now = datetime.today() + timedelta(hours=9)
        else:
            dt_now = datetime.strptime(display_date,'%Y-%m-%d')

        start = dt_now.replace(hour=0,minute=0,second=0)
        end = dt_now.replace(hour=23,minute=59,second=59)
        baby_events = db.GqlQuery(
            "SELECT * FROM BabyEvent "
            "WHERE enable = TRUE AND timestamp >= :1 AND timestamp <= :2 ORDER BY timestamp DESC",
            start, end)

        stats = {}
        total = {}
        for b_event in baby_events:
            if not b_event.eventType in stats:
                stats[b_event.eventType] = {}
            if not b_event.value in stats[b_event.eventType]:
                stats[b_event.eventType][b_event.value] = 0
            stats[b_event.eventType][b_event.value]+=1

            if not b_event.eventType in total:
                total[b_event.eventType]=0
            total[b_event.eventType]+=1

        milk_total = 0
        if 'formula' in stats:
            for milkvalues in stats['formula'].keys():
                milk_total += stats['formula'][milkvalues] * int(milkvalues[:-2])

        dt_yes = (dt_now + timedelta(days=-1)).strftime('%Y-%m-%d')
        dt_tom = (dt_now + timedelta(days= 1)).strftime('%Y-%m-%d')
        template_values = \
            {
                'stats': stats,
                'total': total,
                'milktotal': milk_total,
                'dt_now': dt_now,
                'dt_yes': dt_yes,
                'dt_tom': dt_tom,
            }
        self.write_template('stat.html', template_values)


class EventAverage(BasePage):
    def get(self):
        from_date = self.request.get('fromdate')
        to_date = self.request.get('todate')

        dt_now = datetime.today() + timedelta(hours=9)

        if not from_date or not to_date:
            dt_from = dt_now - timedelta(days=6)
            dt_to = dt_now
        else:
            dt_from = datetime.strptime(from_date, '%Y-%m-%d')
            dt_to = datetime.strptime(to_date, '%Y-%m-%d')

        dt_from = dt_from.replace(hour=0, minute=0, second=0)
        dt_to = dt_to.replace(hour=23, minute=59, second=59)

        baby_events = db.GqlQuery(
            "SELECT * FROM BabyEvent "
            "WHERE enable = TRUE AND timestamp >= :1 AND timestamp <= :2",
            dt_from, dt_to)

        days = (dt_to - dt_from).days + 1
        stats = {}
        total = {}
        for b_event in baby_events:
            if not b_event.eventType in stats:
                stats[b_event.eventType] = {}
            if not b_event.value in stats[b_event.eventType]:
                stats[b_event.eventType][b_event.value] = 0
            stats[b_event.eventType][b_event.value] += 1

            if not b_event.eventType in total:
                total[b_event.eventType] = 0
            total[b_event.eventType] += 1

        milk_total = 0
        if 'formula' in stats:
            for milkvalues in stats['formula'].keys():
                milk_total += stats['formula'][milkvalues] * int(milkvalues[:-2])

        template_values = \
            {
                'stats': stats,
                'total': total,
                'milktotal': milk_total,
                'dt_from': dt_from.date(),
                'dt_to': dt_to.date(),
                'days': days,
            }
        self.write_template('avg.html', template_values)


class EventGraph(BasePage):
    def get(self):
        from_date = self.request.get('fromdate')
        to_date = self.request.get('todate')

        dt_now = datetime.today() + timedelta(hours=9)

        if not from_date or not to_date:
            dt_from = dt_now - timedelta(days=6)
            dt_to = dt_now
        else:
            dt_from = datetime.strptime(from_date, '%Y-%m-%d')
            dt_to = datetime.strptime(to_date, '%Y-%m-%d')

        dt_from = dt_from.replace(hour=0, minute=0, second=0)
        dt_to = dt_to.replace(hour=23, minute=59, second=59)

        baby_events = db.GqlQuery(
            "SELECT * FROM BabyEvent "
            "WHERE enable = TRUE AND timestamp >= :1 AND timestamp <= :2",
            dt_from, dt_to)

        days = (dt_to - dt_from).days + 1
        total = {}
        value_str = \
            {
                'date': '',
            }
        dt_temp = dt_from.date()
        for key in ['pee', 'boo', 'milk', 'formula']:
            total[key] = {}
            value_str[key] = ''
            for i in range(0, days):
                total[key][dt_temp + timedelta(days=i)] = 0

        for b_event in baby_events:
            if b_event.eventType in total:
                if b_event.timestamp.date() in total[b_event.eventType]:
                    if b_event.eventType == 'formula':
                        total[b_event.eventType][b_event.timestamp.date()] += int(b_event.value[:-2])
                    else:
                        total[b_event.eventType][b_event.timestamp.date()] += 1

        for i in range(0, days):
            dt_temp2 = (dt_temp + timedelta(days=i))
            value_str['date'] += '"' + str(dt_temp2.month) + '/' + str(dt_temp2.day) + '",'
            for key in ['pee', 'boo', 'milk', 'formula']:
                value_str[key] += str(total[key][dt_temp2]) + ','

        template_values = \
            {
                'value_str': value_str,
                'dt_from': dt_from.date(),
                'dt_to': dt_to.date(),
                'days': days,
            }
        self.write_template('graph.html', template_values)


class TSVOutput(BasePage):
    def get(self):
        display_date = self.request.get('date')
        if not display_date:
            dt_now = datetime.today() + timedelta(hours=9)
        else:
            dt_now = datetime.strptime(display_date, '%Y-%m-%d')

        start = dt_now.replace(hour=0, minute=0, second=0)
        end = dt_now.replace(hour=23, minute=59, second=59)
        baby_events = db.GqlQuery(
            "SELECT * FROM BabyEvent "
            "WHERE enable = TRUE AND timestamp >= :1 AND timestamp <= :2 ORDER BY timestamp DESC",
            start, end)
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
    [
        ('/', MainPage),
        ('/save', EventSave),
        ('/history', EventHistory),
        ('/tsv', TSVOutput),
        ('/delete', DeleteEvent),
        ('/stat', EventStatistics),
        ('/avg', EventAverage),
        ('/graph', EventGraph),
    ],
    debug=True)


def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()

