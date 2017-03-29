from google.appengine.api import users
from google.appengine.ext import ndb
from google.appengine.api import memcache
from datetime import datetime
import logging
import re

NOTFOUND_ID = 0
MAIN_ID = 1
SEND_OK = 2
SEND_FAIL = 3

##############################################

class Admin(ndb.Model):
    user = ndb.UserProperty(auto_current_user_add=False)

def check_self_admin():
    user = users.get_current_user()
    if not user:
        return None
    admin_ent = Admin.get_by_id(user.email())
    if admin_ent:
        if not admin_ent.user:
            admin_ent.user = user
            admin_ent.put()
        return admin_ent.user;
    else:
        return None;

def set_default_admin(default_email='brianhh.lin@gmail.com'):
    admin_ent = Admin.get_by_id(default_email)
    if not admin_ent:
        admin_ent = Admin(id=default_email)
        admin_ent.user = None
        admin_ent.put()

##############################################

class PageView(ndb.Model):
    english_title = ndb.StringProperty(indexed=False)
    title = ndb.StringProperty(indexed=False)
    author = ndb.StringProperty(indexed=False)
    date = ndb.DateProperty(auto_now_add=True)
    summary = ndb.StringProperty(indexed=False)
    content = ndb.StringProperty(indexed=False)

def pageview_key(type_name):
    return ndb.Key('PageView', type_name)

def update_pageview(type_name, english_title, title, author, date, summary, content, page_id):
    p = PageView()
    if page_id == "":
        slug = (type_name + ' ' + date + ' ' + english_title).lower()
        slug = re.sub('[^0-9a-zA-Z]+', '-', slug).strip(' \t\n\r-')
        p = PageView(parent=pageview_key(type_name), id=slug)
    else:
        p = PageView.get_by_id(page_id, parent=pageview_key(type_name))
    p.english_title = english_title
    p.title = title
    p.author = author
    p.summary = summary
    p.content = content
    try:
        p.date = datetime.strptime(date, '%m/%d/%Y')
    except:
        p.date = datetime.strptime(date, '%Y-%m-%d')
    p.put()

def get_pages_init(type_name, num):
    try:
        return PageView.query(ancestor=pageview_key(type_name)).order(-PageView.date).fetch_page(num)
    except:
        return None, None, None

def get_pages_next(type_name, cursor, num):
    try:
        return PageView.query(ancestor=pageview_key(type_name)).order(-PageView.date).fetch_page(num, start_cursor=cursor)
    except:
        return None, None, None

def get_pages_prev(type_name, cursor, num):
    try:
        return PageView.query(ancestor=pageview_key(type_name)).order(PageView.date).fetch_page(num, start_cursor=cursor)
    except:
        return None, None, None

def get_page(page_id):
    type_name = page_id.split('-')[0]
    try:
        p = PageView.get_by_id(id=page_id, parent=pageview_key(type_name))
        return p
    except:
        return None

def delete_page(page_id):
    try:
        get_page(page_id).key.delete()
    except:
        pass

##############################################

def update_component(key_id, index, head, body, html):
    c = Component.get_by_id(int(key_id))
    if c:
        try:
            c.index = int(index)
            c.head = head
            c.body = body
            c.html = html
            c.put()
        except:
            pass

def set_page_component(page_id, index, head, body, html):
    try:
        c = Component()
        c.page_id = page_id
        c.index = index
        c.head = head
        c.body = body
        c.html = html
        c.put()
    except:
        pass

def set_notfound_component():
    q = get_component_query(NOTFOUND_ID)
    if q.count(1) > 0:
        return
    html = '<div id="mycarousel" class="carousel slide hidden-xs" data-ride="carousel">' \
                '<div class="carousel-inner">' \
                    '<div class="item active">' \
                    ' <img src="https://i.imgur.com/NggXAPF.jpg?2" alt="" class="img-responsive">' \
                        '<div class="carousel-caption">' \
                        '<h3>"Always be prepared to give an answer to everyone who asks you to give the reason for  the hope that you have. But do this with gentleness and respect"</h3>' \
                        '<p>1 Peter 3:15</p>' \
                        '</div>' \
                    '</div>' \
                '</div>' \
            '</div>' \
            '<h2 class="text-center">Oops!</h2>' \
            '<p class="text-center">We cannot find  the page for you.</p>'
    set_page_component(NOTFOUND_ID, 0, None, None, html)

##############################################

class Page(ndb.Model):
    group = ndb.StringProperty()
    index = ndb.IntegerProperty()
    text = ndb.StringProperty()
    slug = ndb.StringProperty()

def get_page_by_id(key_id):
    try:
        p = Page.get_by_id(int(key_id))
        return p
    except:
        logging.info("No page with this id: "+str(key_id))

def get_page_by_slug(slug):
    try:
        q = Page.query(Page.slug == str(slug)).order(Page.index)
        result = q.fetch(1)
        if len(result) == 1:
            return result[0]
        else:
            return None
    except:
        return None

def get_pages_by_group(group):
    try:
        q = Page.query(Page.group == str(group)).order(Page.index)
        return q
    except:
        return None

def update_page(key_id, index, text, slug):
    p = Page.get_by_id(int(key_id))
    if p.slug != slug:
        if not get_page_by_slug(slug) == None: # Avoid slug collision
            logging.info("Slug collision: " + slug)
            return
    if p:
        try:
            p.index = int(index)
            p.text = text
            p.slug = slug
            p.put()
        except:
            pass

def set_page(group, index, text, slug):
    if not get_page_by_slug(slug) == None: # Avoid slug collision
        logging.info("Slug collision: " + slug)
        return
    p = Page()
    p.group = group
    p.index = index
    p.text = text
    p.slug = slug
    p.put()



