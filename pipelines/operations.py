import logging
import pickle
import time
import uuid

import requests
from bs4 import BeautifulSoup
from peewee import IntegrityError
from selenium import webdriver

from models.domain import Flight as DomainFlight
from models.entities import Flight, Note
from persistence import cache
from pipelines import creatable
from pipelines.pipeline import Operation, OperationState


@creatable
class AirportDataScrapper(Operation):
    """Scraps data for airport flights
    """
    _save_to = None

    def __init__(self, save_to):
        self._save_to = save_to

    def execute(self, op_state: OperationState):
        logging.debug("Executing AirportDataScrapper...")

        # Replace with a proper JS rendering engine, using selenium for now
        driver = webdriver.Chrome()
        driver.get('https://www.viennaairport.com/passagiere/ankunft__abflug/abfluege')
        time.sleep(1)

        soup = BeautifulSoup(driver.page_source, 'html.parser')

        # Selectors should be configurable, hardcoding for demo purposes
        destinations = soup.select(
            "#flugdaten-abflug > div > div.detail-table > div.fd-detail-rows > "
            + "div > div.detail-table__cell.text-uppercase.fdabf-td2 > span.hidden-xs")
        times = soup.select(
            "#flugdaten-abflug > div > div.detail-table > div.fd-detail-rows >"
            + " div > div.detail-table__cell.text-center.fdabf-td1")

        result = []

        for i in range(len(destinations)):
            result.append(DomainFlight(destinations[i].text, times[i].text))

        op_state.set_property(self._save_to, result)

        return op_state


@creatable
class LocationTemperatureScrapper(Operation):
    """Scraps temperature data given a location
    """
    _fetching_service = None
    _flights = None

    def __init__(self, fetching_service, flights):
        self._fetching_service = fetching_service
        self._flights = flights

    def execute(self, op_state: OperationState):
        logging.debug("Executing LocationTemperatureScrapper...")

        flights = op_state.get_property(self._flights)

        for flight in flights:
            flight.weather = self._fetching_service.get_weather(flight.destination)

        op_state.set_property(self._flights, flights)

        return op_state


@creatable
class CacheSaver(Operation):
    """Caches a record that's passed as a property from operation state
    """
    _key = None
    _property = None

    def __init__(self, prop):
        self._key = str(uuid.uuid4())
        self._property = prop

    def execute(self, op_state: OperationState):
        logging.debug("Executing CacheSaver...")

        cache.set(self._key, pickle.dumps(op_state.get_property(self._property)))
        op_state.set_property("uuid", self._key)

        return op_state


@creatable
class CacheToState(Operation):
    """Moves a record from the cache to the operation state
    """
    _cache_key = None
    _state_key = None

    def __init__(self, cache_key, state_key):
        self._cache_key = cache_key
        self._state_key = state_key

    def execute(self, op_state: OperationState):
        logging.debug("Executing CacheToState...")

        op_state.set_property(self._state_key, pickle.loads(cache.get(self._cache_key)))

        return op_state


@creatable
class PostProcessingInitializer(Operation):
    """Initializes post-processing logic
    """
    _url = None

    def __init__(self, url):
        self._url = url

    def execute(self, op_state: OperationState):
        logging.debug("Executing PostProcessingInitializer...")
        try:
            req_data = {
                'dataUUID': op_state.get_property('uuid')
            }

            requests.post(self._url, json=req_data)

            return op_state

        except KeyError:
            logging.error("Invalid pipeline. Data UUID needs to be supplied before initializing post-processor.")


@creatable
class FlightNoteCreator(Operation):
    _flights = None

    def __init__(self, flights):
        self._flights = flights

    def execute(self, op_state: OperationState):
        logging.debug("Executing FlightNoteCreator...")

        flights = op_state.get_property(self._flights)

        for flight in flights:
            try:
                if float(flight.weather) > 250:
                    flight.add_note("Something something")
                elif 200 < float(flight.weather) < 240:
                    flight.add_note("Wow")
                else:
                    flight.add_note("Boring")
            except ValueError:
                logging.error(
                    "Unable to process record: {}-{}-{}".format(flight.destination, flight.weather, flight.time))

        op_state.set_property(self._flights, flights)

        return op_state


@creatable
class FlightsDatabaseSaver(Operation):
    """Saves the flights data in the database
    """
    _flights = None

    def __init__(self, flights):
        self._flights = flights

    def execute(self, op_state: OperationState):
        logging.debug("Executing DatabaseSaver...")

        flights = op_state.get_property(self._flights)

        for flight in flights:
            try:
                logging.debug("Saving flight: {}-{}-{}".format(flight.destination, flight.weather, flight.time))
                db_flight = Flight.create(destination=flight.destination, weather=flight.weather, timestamp=flight.time)

                if len(flight.notes) > 0:
                    for note in flight.notes:
                        Note.create(text=note, flight=db_flight)

                return op_state

            except IntegrityError:
                logging.error("Unable to save record: {}-{}-{}".format(flight.destination, flight.weather, flight.time))
