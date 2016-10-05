from couchdb.mapping import Document, TextField
from .DBManager import DBManager

class BaseDocument(Document):

    datatype = TextField()

    def __init__(self, id=None, datatype=None, **values):

        if(datatype is None):
            datatype = self.__class__.__name__

        super().__init__ (
            id=id,
            datatype=datatype,
            **values
        )

    def save(self):
        self.store(DBManager.db())
