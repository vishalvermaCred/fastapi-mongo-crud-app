from http import HTTPStatus
import logging
from fastapi.responses import JSONResponse

from app.constants import ResponseKeys
from app.settings import SERVICE_NAME, LOG_LEVEL


def get_logger():
    extra = {"app_name": SERVICE_NAME}
    # format = "[%(asctime)s] %(levelname)s in %(module)s : %(message)s"
    format = "%(levelname)s:     [%(asctime)s] %(module)s: %(message)s"
    logging.basicConfig(level=LOG_LEVEL, format=format)
    logger = logging.getLogger(__name__)
    logger = logging.LoggerAdapter(logger, extra)
    return logger


def generate_response(message, success, code=HTTPStatus.OK, data={}):
    response = {
        ResponseKeys.SUCCESS: success,
        ResponseKeys.MESSAGE: message,
    }
    if data:
        response[ResponseKeys.DATA] = data

    api_response = JSONResponse(response, code)
    return api_response
