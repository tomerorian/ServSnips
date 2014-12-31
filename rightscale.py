import json
import urllib
import urllib2
import getpass
import cookielib
import base64
import logging

log = logging.getLogger(__name__)


class RightScaleClient(object):
    def __init__(self, account_id=37370, rs_user="no_user@gmail.com", debug=False, interactive=False, rs_password=None):
        self._debug = debug
        self.rs_account_id = account_id
        self.rs_user = rs_user
        self.interactive = interactive
        if rs_password is None:
            self.rs_password = getpass.getpass("Enter rightscale password for user %s: " % rs_user)
        else:
            self.rs_password = rs_password

        self._is_prepared = False
    
    def prepare(self):
        if not self._is_prepared:
            self._init_url_opening()
            self.login()
            self._is_prepared = True
        
    RS_BASE_URL = "https://us-4.rightscale.com/"
    _stuff_at_the_end = "?api_version=1.0&format=js"

    def _get(self, relative_uri):
        uri_prefix = "api/acct/%s" % self.rs_account_id
        url = self.RS_BASE_URL + uri_prefix + relative_uri + self._stuff_at_the_end
        d = self._opener.open(url).read()
        return json.loads(d)

    def get_server_list(self):
        url = self.RS_BASE_URL + "api/acct/%s/servers?api_version=1.0&format=js" % self.rs_account_id
        d = self._opener.open(url).read()
        return json.loads(d)

    def get_server_ip(self, server_href):
        return self._get_server(server_href, "/settings")

    def _get_server(self, server_href, relative_uri):
        url = server_href + relative_uri + self._stuff_at_the_end
        d = self._opener.open(url).read()
        return json.loads(d)

    def get_server_monitoring(self, server_href):
        return self._get_server(server_href, "/monitoring")
    
    def get_all_servers_ip(self, keywords, aws_id):
        keywords = [i.lower() for i in keywords]
        servers = self.get_server_list()
        filtered_servers = []
        for s in servers:
            has_keywords = all([k in s['nickname'].lower() for k in keywords])
            if has_keywords:
                filtered_servers.append(s)
        filtered_servers = [i for i in filtered_servers if i['state'] == 'operational']
        print "Fetching IPs for: %s" % [i['nickname'] for i in filtered_servers]
        for s in filtered_servers:
            server_settings = self.get_server_ip(s['href'])
            if aws_id and not (aws_id in server_settings['aws-id']):
                continue
            print s['nickname'], server_settings.get('ip-address'), server_settings.get('aws-id')
        print "Done"
    
    def login(self):
        url = self.RS_BASE_URL + "api/acct/%s/login?api_version=1.0" % self.rs_account_id
        d = self._opener.open(url).read()
        return d
    
    def _init_url_opening(self):
        cookie_handler = urllib2.HTTPCookieProcessor(cookielib.CookieJar(policy=cookielib.DefaultCookiePolicy()))
        no_redirect = NoRedirectHandler()
        handlers = [cookie_handler, no_redirect]
        if self._debug:
            debug_handler = urllib2.HTTPSHandler(debuglevel=1)
            handlers.append(debug_handler)
        self._opener = urllib2.build_opener(*handlers)
        self._opener.addheaders.append(('Authorization', 'Basic ' + base64.b64encode(self.rs_user + ':' + self.rs_password)))
        self._opener.addheaders.append(('X-API-VERSION', 1.0))


class NoRedirectHandler(urllib2.HTTPRedirectHandler):     
    def http_error_301(self, req, fp, code, msg, headers):  
        print "not redirecting 301"
        return

    def http_error_302(self, req, fp, code, msg, headers):   
        print "not redirecting 302"
        return
