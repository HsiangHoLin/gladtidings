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
models.set_default_admin('test@example.com') # TODO

def is_admin():
    admin_info = models.check_self_admin();
    if admin_info:
        return True
    else:
        return False

def handle_404(webapp):
    template = JINJA_ENVIRONMENT.get_template('static/404.html')
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
        }

        template = JINJA_ENVIRONMENT.get_template('templates/editpage.html')
        self.response.write(template.render(template_values))

class SubmitPage(webapp2.RequestHandler):

    def post(self):
        if not is_admin():
            self.response.out.write("oops")
            self.response.set_status(404)
            return

        type_name = self.request.get('type_name')
        if not type_name:
            self.response.out.write("oops")
            self.response.set_status(404)
            return

        page_id = self.request.get("page_id")
        english_title = self.request.get('english_title')
        title = self.request.get('title')
        author = self.request.get('author')
        date = self.request.get('date')
        summary = self.request.get('summary')
        content = self.request.get('content')
        models.update_pageview(type_name, english_title, title, author, date, summary, content, page_id)
        self.redirect('/events')

class DeletePage(webapp2.RequestHandler):

    def post(self):
        if not is_admin():
            self.response.out.write("oops")
            self.response.set_status(404)
            return

        page_id = self.request.get("page_id")
        models.delete_page(page_id)
        self.redirect('/events')

class Events(webapp2.RequestHandler):

    def get(self):

        def cursor_pagination(prev_cursor_str, next_cursor_str):
            PAGE_SIZE = 3
            if not prev_cursor_str and not next_cursor_str:
                p, next_cursor, more = models.get_pages_init('event', PAGE_SIZE)
                prev_cursor_str = ''
                if next_cursor:
                    next_cursor_str = next_cursor.urlsafe()
                else:
                    next_cursor_str = ''
                next_ = True if more else False
                prev_ = False
            elif next_cursor_str:
                cursor = Cursor(urlsafe=next_cursor_str)
                p, next_cursor, more = models.get_pages_next('event', cursor, PAGE_SIZE)
                prev_cursor_str = next_cursor_str
                next_cursor_str = next_cursor.urlsafe()
                prev_ = True
                next_ = True if more else False
            elif prev_cursor_str:
                cursor = Cursor(urlsafe=prev_cursor_str)
                p, next_cursor, more = models.get_pages_prev('event', cursor, PAGE_SIZE)
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

        #cursor = Cursor(urlsafe=self.request.get('cursor'))
        #show_admin = is_admin()
        #page_query = models.get_pages('event')
        #page_query.fetch(
        #itr = page_query.iter(produce_cursors=True, start_cursor=cursor, batch_size=BATCH_SIZE)
        #template_values = {
        #    'show_admin': show_admin,
        #    'page_query': page_query
        #    'prev_cursor': try_prev(itr)
        #    'next_cursor': try_next(itr)
        #}
        #template = JINJA_ENVIRONMENT.get_template('templates/events.html')
        #self.response.write(template.render(template_values))

        show_admin = is_admin()
        prev_cursor = self.request.get('prev_cursor', '')
        next_cursor = self.request.get('next_cursor', '')
        p, prev_cursor_str, next_cursor_str, prev_, next_ = cursor_pagination(prev_cursor, next_cursor)

        template_values = {
            'show_admin': show_admin,
            'pages': p,
            'has_prev' : prev_,
            'has_next' : next_,
            'prev_cursor': prev_cursor_str,
            'next_cursor': next_cursor_str,
        }
        template = JINJA_ENVIRONMENT.get_template('templates/events.html')
        self.response.write(template.render(template_values))

class OneEvent(webapp2.RequestHandler):

    def get(self):

        show_admin = is_admin()
        path = self.request.path
        page_id = path.split('/')[2]
        page = models.get_page(page_id)
        template_values = {
            'show_admin': show_admin,
            'page': page,
        }
        template = JINJA_ENVIRONMENT.get_template('templates/oneevent.html')
        self.response.write(template.render(template_values))

class Default(webapp2.RequestHandler):

    def get(self):
        seg = self.request.path.strip("/").split('/')
        if len(seg) != 1:
            self.response.out.write("oops")
            self.response.set_status(404)
            return

        try:
            if seg[0] == '':
                seg[0] = 'index'
            template = JINJA_ENVIRONMENT.get_template('static/%s.html' % seg[0])
            self.response.out.write(template.render())
        except:
            handle_404(self)
            return


# [START app]
app = webapp2.WSGIApplication([
    ('/login/editpage', EditPage),
    ('/login/submitpage', SubmitPage),
    ('/login/deletepage', DeletePage),
    ('/events/*', Events),
    ('/event/[0-9a-zA-Z].*', OneEvent),
    ('/.*', Default),
], debug=True)
# [END app]
