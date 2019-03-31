import pytest
import handler
import json
from pytest_mock import mocker


def test_geohash_success():
    assert handler.geohash(37.421542, -122.085589, b'2005-05-26-10458.68') == {'latitude': 37.857713, 'longitude': -122.544543}


def test_geohash_string():
    with pytest.raises(TypeError):
        assert handler.geohash(37.421542, -122.085589, '2005-05-26-10458.68') is None


def test_geohash_no_coord():
    with pytest.raises(TypeError):
        assert handler.geohash(None, None, b'2005-05-26-10458.68') is None


def test_geohash_no_date():
    with pytest.raises(TypeError):
        assert handler.geohash(37.421542, -122.085589, None) is None


def test_handler_invalid_url(mocker):
    mocker.patch.object(handler, 'validate_url')
    i = {
        "queryStringParameters": {
            "latitude": "37.421542",
            "longitude": "-122.085589",
            "date": "2005-05-26-10458.68"
        }
    }

    body = {
        'errorMessage': "Error validating URL."
    }

    r = {'statusCode': 500, 'body': json.dumps(body)}
    handler.validate_url.return_value = False
    assert handler.handler(i, '') == r


def test_handler_success(mocker):
    i = {
        "queryStringParameters": {
            "latitude": "37.421542",
            "longitude": "-122.085589",
            "date": "2005-05-26-10458.68"
        }
    }

    coordinates = {"latitude": 37.857713, "longitude": -122.544543}
    url = 'https://www.google.com/maps/place/37.857713,-122.544543'
    body = {
        'coordinates': coordinates,
        'url': url
    }

    r = {'statusCode': 200, 'body': json.dumps(body)}
    assert handler.handler(i, '') == r
