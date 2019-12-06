class Flight:
    _destination = None
    _time = None
    _weather = None
    _notes = None

    def __init__(self, dest, time):
        self._destination = dest
        self._time = time
        self._notes = []

    @property
    def destination(self):
        return self._destination

    @property
    def time(self):
        return self._time

    @property
    def weather(self):
        return self._weather

    @property
    def notes(self):
        return self._notes

    @weather.setter
    def weather(self, weather):
        self._weather = weather

    def add_note(self, note):
        self._notes.append(note)
