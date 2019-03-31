import hashlib
import json
import re


def validate_url(input):
    URL_REGEX = re.compile(r"https?://.*/[a-zA-Z0-9-_,/.]*$", re.UNICODE | re.I)
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
