#!/usr/bin/env python

# [START imports]
import os
import urllib

from google.appengine.api import users
from google.appengine.ext import ndb

import jinja2
import webapp2
import models

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.getcwd()),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)
# [END imports]

DEFAULT_GUESTBOOK_NAME = 'default_guestbook'

models.set_default_admin('brianhh.lin@gmail.com')
models.set_default_admin('test@example.com') # TODO

def is_admin():
    admin_info = models.check_self_admin();
    if admin_info:
        return True
    else:
        return False

# We set a parent key on the 'Greetings' to ensure that they are all
# in the same entity group. Queries across the single entity group
# will be consistent. However, the write rate should be limited to
# ~1/second.

def guestbook_key(guestbook_name=DEFAULT_GUESTBOOK_NAME):
    """Constructs a Datastore key for a Guestbook entity.

    We use guestbook_name as the key.
    """
    return ndb.Key('Guestbook', guestbook_name)


# [START greeting]
class Author(ndb.Model):
    """Sub model for representing an author."""
    identity = ndb.StringProperty(indexed=False)
    email = ndb.StringProperty(indexed=False)


class Greeting(ndb.Model):
    """A main model for representing an individual Guestbook entry."""
    author = ndb.StructuredProperty(Author)
    content = ndb.StringProperty(indexed=False)
    date = ndb.DateTimeProperty(auto_now_add=True)
# [END greeting]


# [START main_page]
class MainPage(webapp2.RequestHandler):

    def get(self):

        if is_admin():
            show_admin = True
        else:
            self.response.out.write("oops")
            return

        guestbook_name = self.request.get('guestbook_name',
                                          DEFAULT_GUESTBOOK_NAME)
        greetings_query = Greeting.query(
            ancestor=guestbook_key(guestbook_name)).order(-Greeting.date)
        greetings = greetings_query.fetch(10)

        user = users.get_current_user()
        if user:
            url = users.create_logout_url(self.request.uri)
            url_linktext = 'Logout'
        else:
            url = users.create_login_url(self.request.uri)
            url_linktext = 'Login'

        template_values = {
            'user': user,
            'greetings': greetings,
            'guestbook_name': urllib.quote_plus(guestbook_name),
            'url': url,
            'url_linktext': url_linktext,
        }

        template = JINJA_ENVIRONMENT.get_template('templates/index.html')
        self.response.write(template.render(template_values))
# [END main_page]


# [START guestbook]
class Guestbook(webapp2.RequestHandler):

    def post(self):
        # We set the same parent key on the 'Greeting' to ensure each
        # Greeting is in the same entity group. Queries across the
        # single entity group will be consistent. However, the write
        # rate to a single entity group should be limited to
        # ~1/second.
        guestbook_name = self.request.get('guestbook_name',
                                          DEFAULT_GUESTBOOK_NAME)
        greeting = Greeting(parent=guestbook_key(guestbook_name))

        if users.get_current_user():
            greeting.author = Author(
                    identity=users.get_current_user().user_id(),
                    email=users.get_current_user().email())

        greeting.content = self.request.get('content')
        #greeting.put()

        query_params = {'guestbook_name': guestbook_name}
        self.redirect('/?' + urllib.urlencode(query_params))
# [END guestbook]

class EditPage(webapp2.RequestHandler):

    def get(self):

        if is_admin():
            show_admin = True
        else:
            self.response.out.write("oops")
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
            return

        type_name = self.request.get('type_name')
        if not type_name:
            self.response.out.write("oops")
            return

        page_id = self.request.get("page_id")
        title = self.request.get('title')
        author = self.request.get('author')
        date = self.request.get('date')
        summary = self.request.get('summary')
        content = self.request.get('content')
        models.update_pageview(type_name, title, author, date, summary, content, page_id)
        self.redirect('/event')

class DeletePage(webapp2.RequestHandler):

    def post(self):
        if not is_admin():
            self.response.out.write("oops")
            return

        page_id = self.request.get("page_id")
        models.delete_page(page_id)
        self.redirect('/event')

class Event(webapp2.RequestHandler):

    def get(self):

        show_admin = is_admin()
        page_query = models.get_pages('event')
        template_values = {
            'show_admin': show_admin,
            'page_query': page_query
        }
        template = JINJA_ENVIRONMENT.get_template('templates/event.html')
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


# [START app]
app = webapp2.WSGIApplication([
    ('/login/editpage', EditPage),
    ('/login/submitpage', SubmitPage),
    ('/login/deletepage', DeletePage),
    ('/event/*', Event),
    ('/event/[0-9a-zA-Z].*', OneEvent),
], debug=True)
# [END app]
