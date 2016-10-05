import couchdb
import json
import os

vcap_services = json.loads(os.environ.get('VCAP_SERVICES'))

class DBManager:

    _server_url = vcap_services['cloudantNoSQLDB'][0]['credentials']['url']
    _database_name = "complaint_resolution"
    _db = None
    _server = None

    @classmethod
    def db(cls):
        if (cls._db is None):
            cls._server = couchdb.Server(cls._server_url)
            cls._db = cls._server[cls._database_name]
        return cls._db
