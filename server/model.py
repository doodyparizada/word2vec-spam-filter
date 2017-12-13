import json

from schematics.models import Model
from schematics.types import StringType, ListType, IntType, FloatType, ModelType, DictType


FILENAME = 'db.json'


class DB(Model):
    class ReportedMessage(Model):
        reports = IntType()
        vector = ListType(FloatType)

    reported_messages = DictType(ModelType(ReportedMessage), default={})
    
    def add_new_message(self, reported_message, vector):
        rm = self.ReportedMessage()
        rm.reports = 1
        rm.vector = vector
        self.reported_messages[reported_message] = rm
    
    @classmethod
    def load(cls):
        with open(FILENAME, 'r') as f:
            return DB(json.loads(f.read()))

    def save(self):
        string = json.dumps(self.to_primitive())
        with open(FILENAME, 'w') as f:
            f.write(string)
