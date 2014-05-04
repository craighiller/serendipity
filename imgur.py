#!/usr/bin/env python3
import json, sys, time as dt, pprint, math

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


def main():
    config = None
    try:
        fd = open('config.json', 'r')
    except:
        print("config file [config.json] not found.")
        sys.exit(1)
    try:
        config = json.loads(fd.read())
    except:
        print("invalid json in config file.")
        sys.exit(1)

    factory = Factory(config)

    action = "upload"#sys.argv[1]

    authorized_commands = [
        'upload-auth',
        'comment',
        'vote-gallery',
        'vote-comment'
    ]

    oauth_commands = [
        'credits',
        'refresh',
        'authorize'
    ]

    handle_unauthorized_commands(factory, "upload")
    #if action in authorized_commands:
    #    handle_authorized_commands(factory, action)
    #else:
    #    if action in oauth_commands:
    #        handle_oauth_commands(factory, config, action)
    #    else:
    #        handle_unauthorized_commands(factory, action)

def handle_unauthorized_commands(factory, action):
    imgur = factory.build_api()
    req = None

    if action == 'upload':
        print "swagity"
        req = factory.build_request_upload_from_path(sys.argv[2])
        res = imgur.retrieve(req)
        print "swag"
        print(res['link'])

main()