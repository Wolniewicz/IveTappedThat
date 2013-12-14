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


# We set a parent key on the 'Greetings' to ensure that they are all in the same
# entity group. Queries across the single entity group will be consistent.
# However, the write rate should be limited to ~1/second.

def beerlist_key(beerlist_name=BEER_LIST_NAME):
    """Constructs a Datastore key for a beerlist entity with beerlist_name."""
    return ndb.Key('BeerList', beerlist_name)

class Beer(ndb.Model):
    """Models a basic beer for the beer list, name, abv, brewery"""
    name = ndb.StringProperty()
    abv = ndb.StringProperty()
    brewery = ndb.StringProperty()
    date = ndb.DateTimeProperty(auto_now_add=True)
    author = ndb.UserProperty()


class BeerDB(webapp2.RequestHandler):

    def get(self):

        beerlist_name = self.request.get('beerlist_name', BEER_LIST_NAME)

        beers_query = Beer.query(
            ancestor=beerlist_key(beerlist_name)).order(-Beer.brewery)
        beers = beers_query.fetch(100)

        if users.get_current_user():
            url = users.create_logout_url(self.request.uri)
            url_linktext = 'Logout'
        else:
            url = users.create_login_url(self.request.uri)
            url_linktext = 'Login'

        template_values = {
            'beers': beers,
            'beerlist_name': urllib.quote_plus(beerlist_name),
            'url': url,
            'url_linktext': url_linktext,
        }

        template = JINJA_ENVIRONMENT.get_template('pages/beerDB.html')
        self.response.write(template.render(template_values))


class AddBeer(webapp2.RequestHandler):

    def post(self):
        # We set the same parent key on the 'Greeting' to ensure each Greeting
        # is in the same entity group. Queries across the single entity group
        # will be consistent. However, the write rate to a single entity group
        # should be limited to ~1/second.
        beerlist_name = self.request.get('beerlist_name',
                                          BEER_LIST_NAME)
        beer = Beer(parent=beerlist_key(beerlist_name))

        if users.get_current_user():
            beer.author = users.get_current_user()

        beer.brewery = self.request.get('beerBrewery')
        beer.name = self.request.get('beerName')
        beer.abv = self.request.get('beerABV').replace("%", "");



        if users.get_current_user():
            beer.put()    

        query_params = {'beerlist_name': beerlist_name}
        self.redirect('/beerdb?' + urllib.urlencode(query_params))    


application = webapp2.WSGIApplication([
    ('/beerdb', BeerDB),
    ('/beerdb/addBeer', AddBeer)
], debug=True)