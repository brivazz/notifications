import http
import os
import sys
import time

import requests
from loguru import logger

current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)
from settings import test_settings

if __name__ == '__main__':
    while True:
        try:
            response = requests.get(f'{test_settings.service_url}/api/v1/openapi')
            if response.status_code == http.HTTPStatus.OK:
                logger.info('Services is available!!')
                break
        except requests.exceptions.ConnectionError:
            logger.info('Api is unavailable. Wait...')
        time.sleep(2)
