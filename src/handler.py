import hashlib
import json
import re


def validate_url(input):
    URL_REGEX = re.compile(r"^(?:(?:(?:https?|ftp):)?//)(?:\S+(?::\S*)?@)?(?:(?!(?:10|127)(?:\.\d{1,3}){3})(?!(?:169\.254|192\.168)(?:\.\d{1,3}){2})(?!172\.(?:1[6-9]|2\d|3[0-1])(?:\.\d{1,3}){2})(?:[1-9]\d?|1\d\d|2[01]\d|22[0-3])(?:\.(?:1?\d{1,2}|2[0-4]\d|25[0-5])){2}(?:\.(?:[1-9]\d?|1\d\d|2[0-4]\d|25[0-4]))|(?:(?:[a-z0-9\u00a1-\uffff][a-z0-9\u00a1-\uffff_-]{0,62})?[a-z0-9\u00a1-\uffff]\.)+(?:[a-z\u00a1-\uffff]{2,}\.?))(?::\d{2,5})?(?:[/?#]\S*)?$", re.UNICODE | re.I)
    if re.match(URL_REGEX, input):
        return True
    else:
        return False


def handler(event, context):
    lat = float(event['queryStringParameters']['latitude'])
    lon = float(event['queryStringParameters']['longitude'])
    date = bytes(event['queryStringParameters']['date'], 'utf-8')

    coordinates = geohash(lat, lon, date)

    url = 'https://www.google.com/maps/place/{},{}'.format(coordinates['latitude'], coordinates['longitude'])

    if validate_url(url):
        rc = 200
        body = {
            'coordinates': coordinates,
            'url': url
        }

    else:
        rc = 500
        body = {
            'errorMessage': "Error validating URL."
        }

    return {
        "statusCode": rc,
        "body": json.dumps(body)
    }


def geohash(latitude, longitude, datedow):
    '''Compute geohash() using the Munroe algorithm.
    >>> geohash(37.421542, -122.085589, b'2005-05-26-10458.68')
    37.857713 -122.544543
    '''
    # https://xkcd.com/426/
    h = hashlib.md5(datedow).hexdigest()
    p, q = [('%f' % float.fromhex('0.' + x)) for x in (h[:16], h[16:32])]
    return {'latitude': float('%d%s' % (latitude, p[1:])), 'longitude': float('%d%s' % (longitude, q[1:]))}
