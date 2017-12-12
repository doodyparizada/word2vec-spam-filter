from schematics.models import Model
from schematics.types import StringType, ListType, IntType, FloatType, ModelType, DictType


class DB(Model):
    class ReportedMessage(Model):
        reports = IntType()
        vector = ListType(FloatType)

    reported_messages = DictType(ModelType(ReportedMessage))
    
    def add_new_message(self, reported_message, vector):
        rm = self.ReportedMessage()
        rm.reports = 1
        rm.vector = vector
        self.reported_messages[reported_message] = rm
