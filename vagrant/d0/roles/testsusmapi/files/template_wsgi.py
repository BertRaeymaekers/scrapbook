import functools
import json
import logging
import traceback
import urllib.parse

import pymongo

class MongoRequestProcessor:

    conn = None
    uid = None
    account = None
    def __init__(self, uid, account, connection_string):
        self.uid = uid
        self.account = account
        self.connection_string = connection_string

    def get_mongo_client(self):
        if self.conn:
            # TODO: check if connection is still alive.
            pass
        else:
            self.conn = pymongo.MongoClient(self.connection_string)
        return self.conn

    @functools.lru_cache(maxsize=100, typed=False)
    def get_table_definition(self, module, table):
        collection = self.get_mongo_client().suappconf.UiOrmObject
        return collection.find_one({"module": module, "table": table})

    def do_fetch(self, module, table, primarykey):
        logging.debug("do_fetch(%s, %s, %s)", module, table, primarykey)
        if not isinstance(primarykey, list):
            primarykey = [primarykey]
        table_def = self.get_table_definition(module, table)
        collection = self.get_mongo_client()["0x%s" % self.account][table_def['collection']]
        pk_columns = table_def['pk_columns']
        search_params= {}
        for i in range(len(pk_columns)):
            try:
                search_params[pk_columns[i]] = int(primarykey[i])
            except:
                search_params[pk_columns[i]] = primarykey[i]
        logging.debug("do_fetch search_params: %s", search_params)
        return collection.find_one(search_params)


# Request example: service/fetch?module=modlib.base&table=UiIndividual&key=13&pretty
def fetch(session, fields, json_object):
    """                                                                     
    Fetching an object by TableName[PrimaryKey]                             
    """                                                                     
    try:
        logging.debug("fetch(%s, %s, %s)", session, fields, json_object)
        connection_string="${MONGODB_CONNECTION_STRING}"
        mrp = MongoRequestProcessor(uid=session["userid"], account=session["account"], connection_string=connection_string)
        record = mrp.do_fetch(module=fields['module'][0], table=fields['table'][0], primarykey=fields['key'])
        logging.debug("fetch: %s", record)
        if record:
            try:
                del record['_id']
            except KeyError:
                pass
        logging.debug("fetch: %s", record)
        return (200, "text/json; charset=utf-8", {"result": True, "object": record})
    except Exception as e:                                                  
        # Unknown                                                           
        return (200, "text/json; charset=utf-8", {"result": False, "message": "Object not found (%s: %s)" % (type(e), e), "traceback":  traceback.format_exc().split("\n")})

def application(environ, start_response):
    logging.debug("wsgi.application(%s, .)", environ)
    return_code = 500
    return_mime = "text/json; charset=utf-8"
    path = environ.get('PATH_INFO', '')
    # GET
    params = urllib.parse.parse_qs(environ['QUERY_STRING'])
    # POST
    try:
        request_body_size = int(environ.get('CONTENT_LENGTH', 0))
    except (ValueError):
        request_body_size = 0
    request_body = environ['wsgi.input'].read(request_body_size)
    params.update(urllib.parse.parse_qs(request_body))
    logging.debug("Params: %s", params)
    # Sending to the correct place.
    logging.debug("Path: %s", path)
    if path == "/service/fetch":
        # Dummy session (TO FIX)
        session = {"userid": "bert", "account": "TEST"}
        # Calling fetch.
        (return_code, return_mime, return_object) = fetch(session, params, None)
        logging.debug("Before json.dumps: %s", return_object)
        if "pretty" in params:
             return_message = json.dumps(return_object, sort_keys=True, indent=4, separators=(',', ': '))
        else:
             return_message = json.dumps(return_object)
        # TODO: yield from generator
        return_message = [l.encode("utf-8") for l in return_message.split("\n")]
    else:
        return_mime = "text/html; charset=utf-8"
        return_message = [b"<h1 style='color:blue'>Hello There!</h1>"]
    # Start forming the response
    logging.debug("wsgi.application: %s", return_message)
    start_response('%s OK' % (return_code), [('Content-Type', return_mime)])
    return return_message


logging.basicConfig(filename='logs/susmapi.log',level=logging.DEBUG)

