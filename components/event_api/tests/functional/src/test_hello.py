import http
import logging
import os
import sys

import pytest

current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)
from settings import test_settings

pytestmark = pytest.mark.asyncio


@pytest.mark.parametrize('expected_answer', [{'status': http.HTTPStatus.OK}])
async def test_hello_world(make_get_request, expected_answer: dict):
    url = f'{test_settings.service_url}/api/v1/openapi.json'
    print(url)
    _, status = await make_get_request(url)
    logging.info(f'Response status: {status}')

    assert status == expected_answer['status']
