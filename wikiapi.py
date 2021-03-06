
import random
import requests
import time

from memo import memoize


#### Info for connecting to the api.
API_URL    = "https://en.wikipedia.org/w/api.php"
USER_AGENT = "HOMUNCULUS"
headers    = {'User-Agent': USER_AGENT}

# https://www.mediawiki.org/wiki/API:Query
default = {
    "format": "json",
    "action": "query"
}

# for searching forwards.
outbound_params = {
    "prop": "links",
    "plnamespace": 0,
    "pllimit": "max"
}
outbound_params.update(default)

# for searching backwards.
inbound_params = {
    "prop": "linkshere",
    "lhnamespace": 0,
    "lhlimit": "max",
    "lhprop": "title"
}
inbound_params.update(default)


class WikiAPI(object):
    '''
    WikiAPI provides the underlying functionality for retreiving pages links
    from the Wikipedias mediawiki.org api service.
    '''
    def __init__(self, print_requests=False):
        self.print_requests = print_requests
        self.outbound_requests = 0
        self.inbound_requests = 0
        self.outbound_params  = outbound_params
        self.inbound_params = inbound_params

    def links(self, title, inbound=False):
        '''
        For a given article return a list of links to or from it based
        on if kwarg inbound is set to True or False. These correspond to
        the "linkshere" or "links" properties of the WikiMedia api.
        '''
        return list(self.page_links(title, inbound))

    def random_sample(self, n=1):
        '''
        return a n sized list of random page titles.
        Reference: https://www.mediawiki.org/wiki/API:Random
        '''
        params = {'list': 'random', 'rnnamespace': 0, 'rnlimit': n}
        params.update(default)
        request = requests.get(API_URL, params=params, headers=headers).json()
        return [page['title'] for page in request['query']['random']]

    @memoize
    def page_links(self, title, inbound):
        '''
        Make a request to the Wikipedia API using the given search
        parameters. Returns a parsed dict of the JSON response.
        '''
        params = (inbound_params if inbound else outbound_params)
        params["titles"] = title
        # iteraterate through the results of our query.
        for result in self._query(params):
            node = next(iter(result['pages'].values()))
            # if there isnt any links like can happen exit the gen loop.
            if not params["prop"] in node:
                print("Page missing results? '%s'" % title)
                # Page has no results so exit the generator to yeild nothing
                return
            links = [n["title"] for n in node[params["prop"]]]
            # shuffle to stop the results being completely aphabetical.
            random.shuffle(links)
            # emit the links gathered.
            for link in links:
                yield link

    def _query(self, request):
        '''
        Generator function for retrieving links from wikimedia API whilst
        keeping track of request counts. Reference:
        https://www.mediawiki.org/wiki/API:Query
        '''
        lastContinue = {}
        while True:
            # Balancing requests between forward and 
            if request["prop"] == 'links':
                self.outbound_requests += 1
            else:
                self.inbound_requests += 1
            # Clone original request
            req = request.copy()
            if self.print_requests:
                print("request: " + req["titles"])
            # Modify it with the values returned in the 'continue' section
            # of the last result.
            req.update(lastContinue)
            # Call API
            result = self._fetch_result(req)
            if 'error' in result:
                raise Error(result['error'])
            if 'warnings' in result:
                print(result['warnings'])
            if 'query' in result:
                if len(result['query']) != 0:
                    yield result['query']
            if 'continue' not in result:
                break
            lastContinue = result['continue']

    def _fetch_result(self, params, pause=3, limit=3):
        '''Wrapper around requests to stop instant failure in case of 
        requests.exceptions.ConnectionError. function retries connection
        for a given limit of retries. If connection cannot be established
        original error is thrown.'''
        attempts = 0
        while True:
            try:
                return requests.get(API_URL, params=params, headers=headers).json()
            except requests.exceptions.ConnectionError as e:
                # We couldnt connect, wait a few seconds...
                attempts += 1
                if attempts < limit:
                    print(e.__class__.__name__, "Waiting to reconnect...")
                    time.sleep(pause)
                else:
                    raise requests.exceptions.ConnectionError

