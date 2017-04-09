#!/usr/bin/env python

import os
import urllib

from google.appengine.api import users
from google.appengine.ext import ndb
from google.appengine.datastore.datastore_query import Cursor

import jinja2
import webapp2
import models

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.getcwd()),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

models.set_default_admin('brianhh.lin@gmail.com')

def is_admin():
    admin_info = models.check_self_admin();
    if admin_info:
        return True
    else:
        return False

def handle_404(webapp):
    template = JINJA_ENVIRONMENT.get_template('public/404.html')
    webapp.response.out.write(template.render())
    webapp.response.set_status(404)

class EditPage(webapp2.RequestHandler):

    def get(self):

        if is_admin():
            show_admin = True
        else:
            handle_404(self)
            return

        type_name = self.request.get("type_name")
        page_id = self.request.get("page_id")
        page = models.get_page(page_id)

        template_values = {
            "type_name": type_name,
            "page": page,
            'user_email': models.get_user_email(),
            'is_member_or_admin': is_admin(),
        }

        template = JINJA_ENVIRONMENT.get_template('templates/editpage.html')
        self.response.write(template.render(template_values))

class SubmitPage(webapp2.RequestHandler):

    def post(self):
        if not is_admin():
            handle_404(self)
            return

        type_name = self.request.get('type_name')
        if not type_name:
            handle_404(self)
            return

        page_id = self.request.get("page_id")
        english_title = self.request.get('english_title')
        title = self.request.get('title')
        author = self.request.get('author')
        date = self.request.get('date')
        summary = self.request.get('summary')
        content = self.request.get('content')
        models.update_pageview(type_name, english_title, title, author, date, summary, content, page_id)
        self.redirect('/'+type_name+'s')

class Login(webapp2.RequestHandler):

    def get(self):
        self.redirect('/')

class DeletePage(webapp2.RequestHandler):

    def post(self):
        if not is_admin():
            handle_404(self)
            return

        page_id = self.request.get("page_id")
        models.delete_page(page_id)
        self.redirect('/events')

class Pages(webapp2.RequestHandler):

    type_name = ''
    template_file = ''

    def get(self):

        def cursor_pagination(prev_cursor_str, next_cursor_str):
            PAGE_SIZE = 20
            if not prev_cursor_str and not next_cursor_str:
                p, next_cursor, more = models.get_pages_init(self.type_name, PAGE_SIZE)
                prev_cursor_str = ''
                if next_cursor:
                    next_cursor_str = next_cursor.urlsafe()
                else:
                    next_cursor_str = ''
                next_ = True if more else False
                prev_ = False
            elif next_cursor_str:
                cursor = Cursor(urlsafe=next_cursor_str)
                p, next_cursor, more = models.get_pages_next(self.type_name, cursor, PAGE_SIZE)
                prev_cursor_str = next_cursor_str
                next_cursor_str = next_cursor.urlsafe()
                prev_ = True
                next_ = True if more else False
            elif prev_cursor_str:
                cursor = Cursor(urlsafe=prev_cursor_str)
                p, next_cursor, more = models.get_pages_prev(self.type_name, cursor, PAGE_SIZE)
                p.reverse()
                next_cursor_str = prev_cursor_str
                prev_cursor_str = next_cursor.urlsafe()
                prev_ = True if more else False
                next_ = True
            return p, \
                    prev_cursor_str, \
                    next_cursor_str, \
                    prev_, \
                    next_

        show_admin = is_admin()
        prev_cursor = self.request.get('prev_cursor', '')
        next_cursor = self.request.get('next_cursor', '')
        p, prev_cursor_str, next_cursor_str, prev_, next_ = cursor_pagination(prev_cursor, next_cursor)

        template_values = {
            'type_name': self.type_name,
            'show_admin': show_admin,
            'pages': p,
            'has_prev' : prev_,
            'has_next' : next_,
            'prev_cursor': prev_cursor_str,
            'next_cursor': next_cursor_str,
            'user_email': models.get_user_email(),
            'is_member_or_admin': is_admin(),
        }
        template = JINJA_ENVIRONMENT.get_template(self.template_file)
        self.response.write(template.render(template_values))

class Events(Pages):

    type_name = 'event'
    template_file = 'templates/events.html'

class Articles(Pages):

    type_name = 'article'
    template_file = 'templates/articles.html'

class OnePage(webapp2.RequestHandler):

    type_name = ''
    template_file = ''

    def get(self):

        show_admin = is_admin()
        path = self.request.path
        page_id = path.split('/')[2]
        page = models.get_page(page_id)
        template_values = {
            'show_admin': show_admin,
            'type_name': self.type_name,
            'page': page,
            'user_email': models.get_user_email(),
            'is_member_or_admin': is_admin(),
        }
        template = JINJA_ENVIRONMENT.get_template(self.template_file)
        self.response.write(template.render(template_values))

class OneEvent(OnePage):

    type_name = 'event'
    template_file = 'templates/oneevent.html'

class OneArticle(OnePage):

    type_name = 'article'
    template_file = 'templates/onearticle.html'

class Homepage(webapp2.RequestHandler):

    def get(self):
        PAGE_SIZE = 3
        events, _, _ = models.get_pages_init('event', PAGE_SIZE)
        articles, _, _ = models.get_pages_init('article', PAGE_SIZE)
        template_values = {
            'events': events,
            'articles': articles,
            'user_email': models.get_user_email(),
            'is_member_or_admin': is_admin(),
        }
        template = JINJA_ENVIRONMENT.get_template('templates/index.html')
        self.response.write(template.render(template_values))

class Default(webapp2.RequestHandler):

    def get(self):
        seg = self.request.path.strip("/").split('/')
        if len(seg) != 1:
            handle_404(self)
            return

        try:
            template_values = {
                'user_email': models.get_user_email(),
                'is_member_or_admin': is_admin(),
            }
            template = JINJA_ENVIRONMENT.get_template('public/%s.html' % seg[0])
            self.response.out.write(template.render(template_values))
        except:
            handle_404(self)
            return

class Manage(webapp2.RequestHandler):

    def get(self):
        template_values = {
            'is_admin': is_admin(),
            'admins': models.get_admins(),
            'members': models.get_members(),
            'user_email': models.get_user_email(),
            'is_member_or_admin': is_admin(),
        }
        template = JINJA_ENVIRONMENT.get_template('templates/manage.html')
        self.response.write(template.render(template_values))

# [START app]
app = webapp2.WSGIApplication([
    ('//*', Homepage),
    ('/login', Login),
    ('/login/editpage', EditPage),
    ('/login/submitpage', SubmitPage),
    ('/login/deletepage', DeletePage),
    ('/login/manage', Manage),
    ('/events/*', Events),
    ('/event/[0-9a-zA-Z].*', OneEvent),
    ('/articles/*', Articles),
    ('/article/[0-9a-zA-Z].*', OneArticle),
    ('/.*', Default),
], debug=True)
# [END app]
