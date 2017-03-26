from google.appengine.api import users
from google.appengine.ext import ndb
from google.appengine.api import memcache
from datetime import datetime
import logging

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
    title = ndb.StringProperty(indexed=False)
    author = ndb.StringProperty(indexed=False)
    date = ndb.DateProperty(auto_now_add=True)
    summary = ndb.StringProperty(indexed=False)
    content = ndb.StringProperty(indexed=False)

def pageview_key(type_name):
    return ndb.Key('PageView', type_name)

def delete_pageview(key_id):
    e = ndb.Key('PageView', int(key_id))
    if e:
        e.delete()

def update_pageview(type_name, title, author, date, summary, content, key_id = ""):
    p = PageView()
    if key_id == "":
        p = PageView(parent=pageview_key(type_name))
    else:
        p = PageView.get_by_id(int(key_id))
    p.title = title
    p.author = author
    p.summary = summary
    p.content = content
    p.date = datetime.strptime(date, '%Y-%m-%d')
    p.put()

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

def delete_page(key_id):
    p = ndb.Key('Page',int(key_id))
    if p:
        p.delete()
    cquery = get_component_query(int(key_id))
    for c in cquery.fetch():
        c.key.delete()


