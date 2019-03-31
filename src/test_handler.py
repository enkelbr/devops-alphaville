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
    mocker.patch.object(handler, 'validate_url')
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
    handler.validate_url.assert_called_once_with('https://www.google.com/maps/place/37.857713,-122.544543')


# Invalid URLS
def test_validate_url_nok_malformed_http():
    assert handler.validate_url('http/:/asdf.com/') is False


def test_validate_url_nok_malformed_https():
    assert handler.validate_url('https/:/fdsa.com') is False


def test_validate_url_nok_hostname_only():
    assert handler.validate_url('example') is False


def test_validate_url_nok_s3():
    assert handler.validate_url('s3://my-bucket/') is False


def test_validate_url_nok_missingtld_http():
    assert handler.validate_url('http://missingtld') is False


def test_validate_url_nok_missingtld_https():
    assert handler.validate_url('https://missingtld') is False


def test_validate_url_nok_protocol_only():
    assert handler.validate_url('http://') is False


def test_validate_url_nok_dot():
    assert handler.validate_url('http://.') is False


def test_validate_url_nok_double_dot():
    assert handler.validate_url('http://..') is False


def test_validate_url_nok_dot_trailing_slash():
    assert handler.validate_url('http://../') is False


def test_validate_url_nok_question():
    assert handler.validate_url('http://?') is False


def test_validate_url_nok_double_question():
    assert handler.validate_url('http://??') is False


def test_validate_url_nok_double_question_trailing_slash():
    assert handler.validate_url('http://??/') is False


def test_validate_url_nok_hash():
    assert handler.validate_url('http://#') is False


def test_validate_url_nok_double_hash():
    assert handler.validate_url('http://##') is False


def test_validate_url_nok_space():
    assert handler.validate_url('http://foo.bar?q=Spaces should be encoded') is False


def test_validate_url_nok_double_slash():
    assert handler.validate_url('//') is False


def test_validate_url_nok_double_slash_a():
    assert handler.validate_url('//a') is False


def test_validate_url_nok_triple_slash_a():
    assert handler.validate_url('///a') is False


def test_validate_url_nok_triple_slash():
    assert handler.validate_url('///') is False


def test_validate_url_nok_proto_triple_slash_a():
    assert handler.validate_url('http:///a') is False


def test_validate_url_nok_domain_only():
    assert handler.validate_url('foo.com') is False


def test_validate_url_nok_rdar():
    assert handler.validate_url('rdar://1234') is False


def test_validate_url_nok_h():
    assert handler.validate_url('h://test') is False


def test_validate_url_nok_space_domain():
    assert handler.validate_url('http:// shouldfail.com') is False


def test_validate_url_nok_no_proto():
    assert handler.validate_url(':// should fail') is False


def test_validate_url_nok_space_paren():
    assert handler.validate_url('http://foo.bar/foo(bar)baz quux') is False


def test_validate_url_nok_ftps():
    assert handler.validate_url('ftps://foo.bar/') is False


def test_validate_url_nok_dash_domain():
    assert handler.validate_url('http://-error-.invalid/') is False


def test_validate_url_nok_start_dash():
    assert handler.validate_url('http://-a.b.co') is False


def test_validate_url_nok_end_dash():
    assert handler.validate_url('http://a.b-.co') is False


def test_validate_url_nok_default_route():
    assert handler.validate_url('http://0.0.0.0') is False


def test_validate_url_nok_long_ip():
    assert handler.validate_url('http://1.1.1.1.1') is False


def test_validate_url_nok_short_ip():
    assert handler.validate_url('http://123.123.123') is False


def test_validate_url_nok_number():
    assert handler.validate_url('http://3628126748') is False


def test_validate_url_nok_start_dot():
    assert handler.validate_url('http://.www.foo.bar/') is False


def test_validate_url_nok_start_end_dot():
    assert handler.validate_url('http://.www.foo.bar./') is False


# Valid URLS
def test_validate_url_ok_normal():
    assert handler.validate_url('http://xkcd.com/353') is True


def test_validate_url_ok_trailing_slash():
    assert handler.validate_url('http://xkcd.com/353/') is True


def test_validate_url_ok_parens():
    assert handler.validate_url('http://foo.com/blah_blah_(wikipedia)') is True


def test_validate_url_ok_double_parens():
    assert handler.validate_url('http://foo.com/blah_blah_(wikipedia)_(again)') is True


def test_validate_url_ok_qs():
    assert handler.validate_url('http://www.example.com/wpstyle/?p=364') is True


def test_validate_url_ok_long_qs():
    assert handler.validate_url('https://www.example.com/foo/?bar=baz&inga=42&quux') is True


def test_validate_url_ok_numeric():
    assert handler.validate_url('http://✪df.ws/123') is True


def test_validate_url_ok_authentication():
    assert handler.validate_url('http://userid:password@example.com') is True


def test_validate_url_ok_authentication_trailing_slash():
    assert handler.validate_url('http://userid:password@example.com/') is True


def test_validate_url_ok_authentication_port():
    assert handler.validate_url('http://userid:password@example.com:8080') is True


def test_validate_url_ok_authentication_port_trailing_slash():
    assert handler.validate_url('http://userid:password@example.com:8080/') is True


def test_validate_url_ok_user():
    assert handler.validate_url('http://userid@example.com') is True


def test_validate_url_ok_user_trailing_slash():
    assert handler.validate_url('http://userid@example.com/') is True


def test_validate_url_ok_user_port():
    assert handler.validate_url('http://userid@example.com:8080') is True


def test_validate_url_ok_user_port_trailing_slash():
    assert handler.validate_url('http://userid@example.com:8080/') is True


def test_validate_url_ok_ip():
    assert handler.validate_url('http://142.42.1.1/') is True


def test_validate_url_ok_ip_port():
    assert handler.validate_url('http://142.42.1.1:8080/') is True


def test_validate_url_ok_dash_china():
    assert handler.validate_url('http://➡.ws/䨹') is True


def test_validate_url_ok_unicode():
    assert handler.validate_url('http://⌘.ws') is True


def test_validate_url_ok_unicode_trailing_slash():
    assert handler.validate_url('http://⌘.ws/') is True


def test_validate_url_ok_anchor():
    assert handler.validate_url('http://foo.com/blah_(wikipedia)#cite-1') is True


def test_validate_url_ok_unicode_in_parens():
    assert handler.validate_url('http://foo.com/unicode_(✪)_in_parens') is True


def test_validate_url_ok_something_after_parens():
    assert handler.validate_url('http://foo.com/(something)?after=parens') is True


def test_validate_url_ok_emoji():
    assert handler.validate_url('http://☺.damowmow.com/') is True


def test_validate_url_ok_anchor_qs():
    assert handler.validate_url('http://code.google.com/events/#&product=browser') is True


def test_validate_url_ok_short():
    assert handler.validate_url('http://j.mp') is True


def test_validate_url_ok_encoded():
    assert handler.validate_url('http://foo.bar/?q=Test%20URL-encoded%20stuff') is True


def test_validate_url_ok_arabic():
    assert handler.validate_url('http://مثال.إختبار') is True


def test_validate_url_ok_china():
    assert handler.validate_url('http://例子.测试') is True


def test_validate_url_ok_regex_from_hell():
    assert handler.validate_url('http://-.~_!$&\'()*+,;=:%40:80%2f::::::@example.com') is True


def test_validate_url_ok_leet():
    assert handler.validate_url('http://1337.net') is True


def test_validate_url_ok_dash_domain():
    assert handler.validate_url('http://a.b-c.de') is True


def test_validate_url_ok_https():
    assert handler.validate_url('https://foo_bar.example.com/') is True


def test_validate_url_nok_double_dash_domain():
    assert handler.validate_url('http://a.b--c.de/') is True


def test_validate_url_nok_end_dot():
    assert handler.validate_url('http://www.foo.bar./') is True
