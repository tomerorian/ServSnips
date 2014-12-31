#!/usr/bin/env python

from workflow import Workflow
import sys

import rightscale
import argparse

class Servers:
    def __init__(self, rsc, wf):
        self._rsc = rsc
        self._wf = wf

    def get_servers(self):
        self._rsc.prepare()
        return self._rsc.get_server_list()

    def get_servers_from_cache(self):
        return self._wf.cached_data("ServSnips_servers", self.get_servers, 0)

class Server:
    def __init__(self, rsc, wf, server):
        self._rsc = rsc
        self._wf = wf
        self._server = server

    def get_ip(self):
        self._rsc.prepare()
        return self._rsc.get_server_ip(self._server["href"]).get('ip-address')

    def get_ip_from_cache(self):
        return self._wf.cached_data("ServSnips_server_ip_" + self._server["nickname"], self.get_ip, 0)

def JustRaise():
    raise Exception()

def main(wf):
    try:
        username = wf.cached_data("ServSnips_username", JustRaise, 0)
        password = wf.cached_data("ServSnips_password", JustRaise, 0)
    except:
        wf.add_item("config your username and password", subtitle="use: ?ip-install username password")
        wf.send_feedback()
        return

    query = wf.args[0]

    rsc = rightscale.RightScaleClient(rs_user=username, rs_password=password) # this takes time and I don't need it every time

    servers = Servers(rsc, wf)

    server_list = [(server["nickname"], Server(rsc, wf, server).get_ip_from_cache()) for server in servers.get_servers_from_cache() if server['state'] == 'operational' and query.lower() in server["nickname"].lower()]

    for server in server_list:
        wf.add_item(server[0] + " [" + server[1] + "]", arg=server[1], valid=True)

    wf.send_feedback()


if __name__ == u"__main__":
    wf = Workflow()
    sys.exit(wf.run(main))