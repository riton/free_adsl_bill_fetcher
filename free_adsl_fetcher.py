#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import os
import sys
import json
import logging
import requests
import HTMLParser

try:
    import http.client as http_client
except ImportError:
        import httplib as http_client

http_client.HTTPConnection.debuglevel = 1

logging.basicConfig()
logging.getLogger().setLevel(logging.DEBUG)
requests_log = logging.getLogger("requests.packages.urllib3")
requests_log.setLevel(logging.DEBUG)
requests_log.propagate = True

class FreeAdslFetcher(object):

    USER_AGENT = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.104 Safari/537.36'
    #LOGIN_URL = 'http://httpbin.org/post'
    LOGIN_URL = 'https://subscribe.free.fr/login/login.pl'
    LOGOUT_URL = 'https://adsl.free.fr/logout.pl'
    LIST_BILLS_URL = 'https://adsl.free.fr/liste-factures.pl'

    class FreeSessionCredentials(object):
        def __init__(this, id, idt):
            this.id = id
            this.idt = idt

        def toDict(this):
            return {'id': this.id, 'idt': this.idt}

        def __str__(this):
            return "id=%s&idt=%s" % (this.id, this.idt)

    def __init__(this, user, password):

        this.user = user
        this.password = password

        this._transaction_creds = None

    def _default_headers(this):
        return {
            'User-Agent': this.USER_AGENT
        }

    def login(this):
        payload = {
            'login': this.user,
            #'login': 'TheLogin',
            #'pass' : 'ThePassword',
            'pass' : this.password,
            'ok'   : 'Valider',
            'link' : ''
        }

        headers = this._default_headers().copy()
        headers.update({
            'Content-Type': 'application/x-www-form-urlencoded'
        })

        r = requests.post(this.LOGIN_URL, headers=headers, data=payload,
                allow_redirects=False)

        location = r.headers['location']
        this._buildSessionCreds(location)

    def _buildSessionCreds(this, url):
        # https://adsl.free.fr/home.pl?id=16779576&idt=1015c62833046b0f
        ids_s = url[url.index('?')+1:]
        h = dict(x.split('=') for x in ids_s.split('&'))
        this._transaction_creds = FreeAdslFetcher.FreeSessionCredentials(id=h['id'], idt=h['idt'])

    def _appendUrlCreds(this, url):
        creds = this._transaction_creds
        return url + '?id=%s&idt=%s' % (creds.id, creds.idt)

    def listBills(this):
        if this._transaction_creds is None: this.login()

        headers = this._default_headers()
        creds = this._transaction_creds
        # We need to build the URL/params by hand.
        # python-requests params doesn't work here
        # it seems that url parameters are order dependant
        url = this._appendUrlCreds(this.LIST_BILLS_URL)
        r = requests.get(url,
                headers=headers,
                allow_redirects=False)

        this._parseBillsList(this.unescapeHTML(r.text))

    @staticmethod
    def unescapeHTML(text):
        return HTMLParser.HTMLParser().unescape(text)

    def _parseBillsList(this, body):
        pat = re.compile(r'<strong>(?P<month>\w+?\s*\d{4})</strong>.*?<strong>(?P<price>\d+(?:\.\d+)? Euros)</strong>.*?<a href="(?P<url>facture_pdf.pl.+?)"', re.S | re.UNICODE)
        r = pat.findall(body)
        for a,b,c in r:
            print "%s :: %s" % (a,b)

    def logout(this):
        if this._transaction_creds is None:
            return
        url = this._appendUrlCreds(this.LOGOUT_URL)
        requests.get(url,
                headers=this._default_headers(),
                allow_redirects=False)
        
    def __enter__(this):
        this.login()
        return this

    def __exit__(this, type, value, traceback):
        this.logout()

def main():

    ids = None
    with open('./ids.json') as f:
        ids = json.load(f)

    with FreeAdslFetcher(ids['login'], ids['password']) as fetcher:
        fetcher.listBills()
    

if __name__ == "__main__":
    main()

