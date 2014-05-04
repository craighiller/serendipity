#!/usr/bin/env python3
import json, sys, time as dt, pprint, math

import imgur_config

from Imgur.Factory import Factory
from Imgur.Auth.Expired import Expired

try:
    from urllib.request import urlopen as UrlLibOpen
    from urllib.request import HTTPError
except ImportError:
    from urllib2 import urlopen as UrlLibOpen
    from urllib2 import HTTPError

def center_pad(s, length):
    num_dashes = float(length - len(s) - 2) / 2
    num_dashes_left = math.floor(num_dashes)
    num_dashes_right = math.ceil(num_dashes)

    return ('=' * num_dashes_left) + ' ' + s + ' ' + ('=' * num_dashes_right)

def two_column_with_period(left, right, length):
    num_periods = (length - (len(left) + len(right) + 2))
    return left + ' ' + ('.' * num_periods) + ' ' + right


def upload(image, name):
    config = imgur_config.config()
    factory = Factory(config)

    action = "upload"

    handle_unauthorized_commands(factory, "upload")

    imgur = factory.build_api()

    req = factory.build_request_upload_from_data(image, name)
    res = imgur.retrieve(req)
    print(res['link'])
