#!/usr/bin/env python3

# fallow grasparkiet
# https://www.2dehands.be/l/dieren-en-toebehoren/vogels-parkieten-en-papegaaien/#q:fallow+grasparkiet

# blackwing grasparkiet
# https://www.2dehands.be/l/dieren-en-toebehoren/vogels-parkieten-en-papegaaien/#q:blackwing+grasparkiet
# https://www.2dehands.be/lrp/api/search?l1CategoryId=395&l2CategoryId=427&limit=30&offset=0&query=blackwing%20grasparkiet&searchInTitleAndDescription=true&viewOptions=list-view

# blackface grasparkiet
# https://www.2dehands.be/l/dieren-en-toebehoren/vogels-parkieten-en-papegaaien/#q:blackface+grasparkiet

import datetime
import json
import sys
import urllib
import urllib3

from typing import Optional, List

import bs4

## https://www.2dehands.be/u/f-f/32011293/

class S2H():
    PROTOCOL = 'https'
    HOST_NAME = 'www.2dehands.be'
    BASE_URL = '%s://%s' % (PROTOCOL, HOST_NAME)

    def __init__(self, category: Optional[List[int]]=None, filters: Optional[List[str]]=None, debug=False):
        if not filters:
            filters = []
        if not category:
            category = []
        self.filters = [filter.replace(' ', '-') for filter in filters]
        self.category = category
        self.debug = debug
        self.filter_string = ""
        self.category_encoded = ""
        self.http = urllib3.PoolManager()

    def get_filter_string(self, force=False):
        if force or not self.filter_string:
            self.filter_string = ''.join(["/%s" % (filter) for filter in self.filters])
        return self.filter_string

    def get_category_encoded(self, force=False):
        if force or not self.category_encoded:
            i=1
            categories = {}
            for category in self.category:
                categories["l%sCategoryId" % (i)] = category
                i += 1
            self.category_encoded = urllib.parse.urlencode(categories)
        return self.category_encoded

    def get_limit_encoded(self, start: int=0, step: int=30):
        return urllib.parse.urlencode({'limit': step, 'offset': start})

    def encode_query(self, query: str) -> str:
        return urllib.parse.urlencode({"query": query})

    def summerize_listing(self, listing):
        result = {
            'id': listing['itemId'],
            'title': listing['title'],
            'description': listing['description'],
            'price': '%s (%.2f)' % (listing['priceInfo']['priceType'], listing['priceInfo']['priceCents']/100),
            'seller': {
                'id': listing['sellerInformation']['sellerId'],
                'name': listing['sellerInformation']['sellerName']
            },
            'url': "%s%s" % (S2H.BASE_URL, listing['vipUrl']),
            'date': listing['date'][:-1], # datetime.datetime.strptime(listing['date'], "%Y-%m-%dT%H:%M:%SZ"),
            'images': []
        }
        if listing['location']['countryName'] == 'België':
            result['location'] = listing['location']['cityName']
        else:
            result['location'] = listing['location']['countryName']
        if 'imageUrls' in listing:
            for imgurl in listing['imageUrls']:
                result['images'].append("%s:%s" % (S2H.PROTOCOL, imgurl))
        return result

    def search(self, query: str):
        step = 30
        position = 0
        total_count = -1
        while total_count < 0 or position < total_count:
            # Using the API
            urlpath = '%s/lrp/api/search?%s&%s&%s&searchInTitleAndDescription=true&viewOptions=list-view' % (S2H.BASE_URL, self.get_category_encoded(), self.get_limit_encoded(start=position, step=step), self.encode_query(query))
            if self.debug: print(urlpath)
            response = self.http.request('GET', urlpath)
            if self.debug: print(response.status)
            if response.status != 200:
                if self.debug: print("Couldn't load '%s', http status code: %s" % (urlpath, response.status))
                # TODO: throw exception
            if self.debug: print(dir(response))
            content_type, temp = response.getheader('content-type').split(';', 1)
            content_type_params = {}
            for param in temp.split(';'):
                key, value = param.strip().split('=', 1)
                content_type_params[key] = value
            if self.debug: print("%s; %s" % (content_type, content_type_params))
            if content_type.lower() == "application/json":
                data = json.loads(response.data) # DeprecationWarning: encoding=content_type_params.get('charset', 'utf-8'))
                total_count = data['totalResultCount']
                listings = data['listings']
                position += len(listings)
                if self.debug: print()
                for listing in listings:
                    yield self.summerize_listing(listing)
            else:
                if self.debug: print("Not JSON!")
                # TODO: throw exception
                position += step


if __name__ == "__main__":
    filters = []
    category = []
    searchstring = None
    arg_mode = ""
    for arg in sys.argv[1:]:
        if not arg_mode:
            if arg.startswith("-"):
                if arg == "--":
                    arg_mode = "--"
                elif arg in ["-f", "--filter"]:
                    arg_mode = "filter"
                elif arg in ["-c", "--category"]:
                    arg_mode = "category" 
            else:
                searchstring = arg
        else:
            if arg_mode == "filter":
                filters.append(arg)
            elif arg_mode == "category":
                category.extend([int(i) for i in arg.split(',')])
            # Resetting arg_mode
            if arg_mode != "--":
                arg_mode = ""

    print("# Searching for '%s' in category: %s" % (searchstring, category))
    if searchstring:
        search = S2H(category=category, filters=filters)
        commands = None
        print()
        for item in search.search(searchstring):
            if not commands:
                commands = "#"
            while commands:
                if commands[0] == "n":
                    # Next
                    commands = commands[1:]
                    break
                elif commands[0] == "h":
                    # Help
                    print("""
                    h   help
                    n   next (also empty)
                    d   details
                    q   quit

                    You can contatenate commands
                    Example:
                        nd  will show you the details of the next one
                    """)
                elif commands[0] == "q":
                    # Quit
                    sys.exit(0)
                elif commands[0] == "d":
                    # Details
                    print("Details:")
                    print(json.dumps(item, indent=4))
                    print()
                else:
                    print("\033[F%s: %s" % (item["id"], item["title"]))
                commands = commands[1:]
                if not commands:
                    commands = input('--> ')
