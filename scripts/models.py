from google.appengine.api import users
from google.appengine.ext import ndb
from google.appengine.api import memcache
from datetime import datetime
import logging
import re

##############################################
class Member(ndb.Model):
    user = ndb.UserProperty(auto_current_user_add=False)

def get_members():
    return Member.query().fetch();

##############################################

class Admin(ndb.Model):
    user = ndb.UserProperty(auto_current_user_add=False)

def get_admins():
    return Admin.query().fetch();

def get_user_email():
    user = users.get_current_user()
    if not user:
        return None
    return user.email()

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

