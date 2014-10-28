#!/usr/bin/env python

import os
import sys
import json
import requests

class FreeAdslFetcher(object):

    USER_AGENT = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.104 Safari/537.36'
    LOGIN_URL = 'https://subscribe.free.fr/login/'

    def __init__(this, user, password):

        this.user = user
        this.password = password

        this._auth_cookie = None

    def _default_headers(this):
        return {
            'User-Agent': this.USER_AGENT
        }

    def _login(this):
        payload = {
            'login': this.user,
            'pass' : this.password
        }
        r = requests.post(this.LOGIN_URL, headers=this._default_headers(), data=payload)
        print r.text


def main():

    ids = None
    with open('./ids.json') as f:
        ids = json.load(f)

    fetcher = FreeAdslFetcher(ids['login'], ids['password'])
    

if __name__ == "__main__":
    main()

