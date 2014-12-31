#!/usr/bin/env python

from workflow import Workflow
import sys

def Default():
    raise Exception("failed to get servers")

def main(wf):
    servers = wf.cached_data("ServSnips_servers", Default, 0)

    for server in servers:
        wf.cache_data("ServSnips_server_ip_" + server["nickname"], None)

    wf.cache_data("ServSnips_servers", None)

if __name__ == u"__main__":
    wf = Workflow()
    sys.exit(wf.run(main))