import logging
import time

import schedule

from pipelines.operations import AirportDataScrapper, LocationTemperatureScrapper, CacheSaver, \
    PostProcessingInitializer
from pipelines.pipeline import Pipeline
from services import OpenWeatherMapFetchingService

if __name__ == '__main__':
    logging.basicConfig()
    logging.getLogger().setLevel(logging.DEBUG)

    pipeline = Pipeline()
    pipeline.add_op(AirportDataScrapper(save_to="flights"))
    pipeline.add_op(LocationTemperatureScrapper(OpenWeatherMapFetchingService, flights="flights"))
    pipeline.add_op(CacheSaver(prop="flights"))
    pipeline.add_op(PostProcessingInitializer("http://localhost:5000/v1/processing/post"))

    logging.debug("Scheduling jobs...")
    schedule.every().hour.do(pipeline.execute)

    while True:
        schedule.run_pending()
        time.sleep(1)
