#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import os
import sys
import json
import logging
import requests
import HTMLParser
from optparse import OptionParser


# try:
#     import http.client as http_client
# except ImportError:
#         import httplib as http_client
# 
# http_client.HTTPConnection.debuglevel = 1
# 
# logging.basicConfig()
# logging.getLogger().setLevel(logging.DEBUG)
# requests_log = logging.getLogger("requests.packages.urllib3")
# requests_log.setLevel(logging.DEBUG)
# requests_log.propagate = True

class HTTPClient(object):

    USER_AGENT = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.104 Safari/537.36'
    
    def __init__(this):
        pass

    def _default_headers(this):
        return {
            'User-Agent': this.USER_AGENT
        }

    def get(this, url, headers={}, *args, **kwargs):
        h = this._default_headers().copy()
        headers.update(h)
        return requests.get(url,
                headers=headers,
                *args, **kwargs)

    def post(this, url, headers={}, *args, **kwargs):
        h = this._default_headers().copy()
        headers.update(h)

        return requests.post(url,
                headers=headers,
                *args, **kwargs)
    
    @staticmethod
    def unescapeHTML(text):
        return HTMLParser.HTMLParser().unescape(text)


class FreeAdslBillFetcher(HTTPClient):

    #LOGIN_URL = 'http://httpbin.org/post'
    LOGIN_URL = 'https://subscribe.free.fr/login/login.pl'
    LOGOUT_URL = 'https://adsl.free.fr/logout.pl'
    BILL_ROOT_URL = 'https://adsl.free.fr'
    LIST_BILLS_URL = BILL_ROOT_URL + '/liste-factures.pl'

    BILLFINDER_RE = re.compile(r'<strong>(?P<month>\w+?\s*\d{4})</strong>.*?<strong>(?P<price>\d+(?:\.\d+)?) Euros</strong>.*?<a href="(?P<url>facture_pdf.pl.+?)"', re.S | re.UNICODE)

    class FreeSessionCredentials(object):
        def __init__(this, id, idt):
            this.id = id
            this.idt = idt

        def toDict(this):
            return {'id': this.id, 'idt': this.idt}

        def __str__(this):
            return "id=%s&idt=%s" % (this.id, this.idt)

    class FreeAdslBill(HTTPClient):
        def __init__(this, title, amount, url):
            this.title = title
            this.amount = amount
            this.url = url

        def __eq__(this, other):
            return this.title == other.title

        def __repr__(this):
            return "FreeAdslBill<%s>" % this.title.encode('utf-8')


    def __init__(this, user, password):

        this.user = user
        this.password = password

        this._transaction_creds = None


    def login(this):
        payload = {
            'login': this.user,
            'pass' : this.password,
            'ok'   : 'Valider',
            'link' : ''
        }

        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        r = this.post(this.LOGIN_URL, headers=headers, data=payload,
                allow_redirects=False)

        location = r.headers['location']
        this._buildSessionCreds(location)

    def _buildSessionCreds(this, url):
        # https://adsl.free.fr/home.pl?id=16779576&idt=1015c62833046b0f
        ids_s = url[url.index('?')+1:]
        h = dict(x.split('=') for x in ids_s.split('&'))
        this._transaction_creds = FreeAdslBillFetcher.FreeSessionCredentials(id=h['id'], idt=h['idt'])

    def _appendUrlCreds(this, url):
        creds = this._transaction_creds
        return url + '?' + str(creds)

    def listBills(this):
        if this._transaction_creds is None: this.login()

        # We need to build the URL/params by hand.
        # python-requests params doesn't work here
        # it seems that url parameters are order dependant
        # on this webservice
        url = this._appendUrlCreds(this.LIST_BILLS_URL)
        r = this.get(url, allow_redirects=False)

        bills = this._parseBillsList(this.unescapeHTML(r.text))
        return bills

    def fetchBill(this, bill):
        # assume that whole PDF fits in memory
        return this.get(bill.url).content

    def writeBillToFile(this, bill, file):
        # assume that whole PDF fits in memory
        with open(file, 'wb') as f:
            f.write(this.fetchBill(bill))


    def _parseBillsList(this, body):
        match = this.BILLFINDER_RE.findall(body)

        bills = []
        for month, price, url in match:
            bills.append(FreeAdslBillFetcher.FreeAdslBill(month, float(price), this.BILL_ROOT_URL + '/' + url))

        return bills

    def logout(this):
        if this._transaction_creds is None:
            return
        url = this._appendUrlCreds(this.LOGOUT_URL)
        this.get(url, allow_redirects=False)
        
    def __enter__(this):
        this.login()
        return this

    def __exit__(this, type, value, traceback):
        this.logout()

class FreeAdslBillFetcherCli(object):


    PROG_NAME = 'free_adsl_fetcher'

    @staticmethod
    def _buildOptParser():
        parser = OptionParser()
        parser.add_option("-p", "--show-price", dest="show_price", default=False,
                action="store_true", help="show price when listing bills")
        parser.add_option("--latest", dest="fetch_latest", default=False,
                action="store_true", help="only fetch latest bill")
        parser.add_option("-c", "--config", dest="config_file",
                default=os.path.expanduser('~') + '/.' + FreeAdslBillFetcherCli.PROG_NAME + '.conf',
                metavar='FILE', help="configuration file")
        parser.add_option("--get", dest="wanted_bills",
                action="append",
                default=[],
                metavar='BILL_TITLE', help="Download bill BILL_TITLE and write it as BILL_TITLE.pdf")
        parser.add_option("-d", "--write-dir", dest="write_directory",
                default='.',
                metavar='DIR', help="write bills to directory DIR")
        parser.add_option("--name-prefix", dest="name_prefix",
                default='',
                metavar='STR', help="prefix each bill filename with STR")
        parser.add_option("--name-suffix", dest="name_suffix",
                default='',
                metavar='STR', help="suffix each bill filename with STR (before PDF extension)")

        return parser

    def parseArgs(this, arg):
        (options, args) = this.opt_parser.parse_args(args=arg)
        this.options = options
        this.args = args

    def __init__(this, args=sys.argv[1:]):
        this.opt_parser = this._buildOptParser()
        this.options = None
        this.args = None
        this.parseArgs(args)

        this.config = this._parseConfigFile(this.options.config_file)
        this.fetcher = None


    def __enter__(this, *args, **kwargs):
        this.fetcher = FreeAdslBillFetcher(this.config['login'], this.config['password'])
        this.fetcher.login()
        return this

    def __exit__(this, type, value, traceback):
        this.fetcher.logout()

    @staticmethod
    def _parseConfigFile(file):
        with open(file) as f:
            return json.load(f)

    def run(this):
        fetched_bills = 0
        wanted_bills = len(this.options.wanted_bills)

        for bill in this.fetcher.listBills():
            bill_filename = this._composeBillFilename(bill)

            if this.options.fetch_latest is True:
                pdf_path = this._fetchBill(bill)
                print "Your latest bill was written to '%s'" % pdf_path
                break

            if wanted_bills > 0:
                if bill.title in [x.decode('utf-8') for x in this.options.wanted_bills]:
                    pdf_path = this._fetchBill(bill)
                    print "%s bill was written to '%s'" % (bill.title, pdf_path)

            else:
                this._printBill(bill)

        sys.exit(0)

    def _printBill(this, bill):
        print "- %s" % bill.title,
        if this.options.show_price:
            print " (%s €)" % bill.amount,
        print ""

    def _composeBillFilename(this, bill):
        bill_filename = this.options.write_directory.rstrip('/') + '/'
        bill_filename += this.options.name_prefix
        bill_filename += re.sub(r'\s+', '_', bill.title)
        bill_filename += this.options.name_suffix + '.pdf'
        return bill_filename

    def _fetchBill(this, bill):
        bill_filename = this._composeBillFilename(bill)
        this.fetcher.writeBillToFile(bill, bill_filename)
        return bill_filename
    

if __name__ == "__main__":
    with FreeAdslBillFetcherCli() as cli:
        cli.run()
