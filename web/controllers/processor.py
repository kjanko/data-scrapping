import logging

from flask import Blueprint, request, abort, make_response

from pipelines.operations import CacheToState, FlightsDatabaseSaver, FlightNoteCreator
from pipelines.pipeline import Pipeline

processing_api = Blueprint('processing_api', __name__)


@processing_api.route('/v1/processing/post', methods=['POST'])
def post_processing():
    if not request.get_json():
        abort(400, 'Bad request: unable to fetch JSON')

    try:
        request_json = request.get_json()

        logging.debug("Postprocessing data ID: {}".format(request_json['dataUUID']))

        pipeline = Pipeline()
        pipeline.add_op(CacheToState(request_json['dataUUID'], "flights"))
        pipeline.add_op(FlightNoteCreator("flights"))
        pipeline.add_op(FlightsDatabaseSaver(flights="flights"))
        pipeline.execute()

        return make_response('OK', 200, {'Content-Type': 'application/json'})

    except (AttributeError, KeyError) as e:
        return make_response("Invalid JSON format. Server said: {}".format(str(e)), 400, {'Content-Type': 'text/plain'})
