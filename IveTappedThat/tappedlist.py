import os
import urllib

from google.appengine.api import users
from google.appengine.ext import ndb

import jinja2
import webapp2


JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)



BEER_LIST_NAME = "beer_list"
NICKNAME =  users.get_current_user().nickname()

# We set a parent key on the 'Greetings' to ensure that they are all in the same
# entity group. Queries across the single entity group will be consistent.
# However, the write rate should be limited to ~1/second.

def beerlist_key(beerlist_name=BEER_LIST_NAME):
    """Constructs a Datastore key for a beerlist entity with beerlist_name."""
    return ndb.Key('BeerList', beerlist_name)

def userTappedList_key(userTappedList_name=NICKNAME):
    """Constructs a Datastore key for a tapped list entity with user name."""
    return ndb.Key('userTappedList', userTappedList_name)

class Beer(ndb.Model):
    """Models a basic beer for the beer list, name, abv, brewery"""
    name = ndb.StringProperty()
    abv = ndb.StringProperty()
    brewery = ndb.StringProperty()
    date = ndb.DateTimeProperty(auto_now_add=True)
    author = ndb.UserProperty()

class UserTappedList(ndb.Model):
    """Models a basic tapped list for a user"""
    beer = Beer
    date = ndb.DateTimeProperty(auto_now_add=True)

class TappedList(webapp2.RequestHandler):

    def get(self):

        beerlist_name = self.request.get('beerlist_name', BEER_LIST_NAME)
        userTappedList_name = self.request.get('userTappedList_name',NICKNAME)

        beers_query = Beer.query(
            ancestor=beerlist_key(beerlist_name)).order(-Beer.brewery)
        beers = beers_query.fetch(10)

        tappedList_query = UserTappedList.query(
            ancestor=userTappedList_key(userTappedList_name)).order(-UserTappedList.date)
        personaltapped = tappedList_query.fetch(10)

        if users.get_current_user():
            url = users.create_logout_url(self.request.uri)
            url_linktext = 'Logout'
        else:
            url = users.create_login_url(self.request.uri)
            url_linktext = 'Login'

        template_values = {
            'beers': beers,
            'beerlist_name': urllib.quote_plus(beerlist_name),
            'personaltapped': personaltapped,
            'userTappedList_name': urllib.quote_plus(userTappedList_name),
            'url': url,
            'url_linktext': url_linktext,
        }

        template = JINJA_ENVIRONMENT.get_template('pages/tappedlist.html')
        self.response.write(template.render(template_values))

#class AddToList(webapp2.RequestHandler):

 #   def post(self):

application = webapp2.WSGIApplication([
    ('/tappedlist', TappedList)
    #('/tappedlist/addtolist', AddToList)
], debug=True)