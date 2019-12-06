from peewee import Model, CharField, ForeignKeyField

from models import database


class BaseModel(Model):
    class Meta:
        database = database


class Flight(BaseModel):
    destination = CharField()
    weather = CharField()
    timestamp = CharField()

    @property
    def notes(self):
        return self.notes.get()


class Note(BaseModel):
    text = CharField()
    flight = ForeignKeyField(Flight, backref='notes')