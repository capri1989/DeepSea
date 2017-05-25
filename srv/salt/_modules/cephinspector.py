# -*- coding: utf-8 -*-
# vim: ts=8 et sw=4 sts=4

import os

def _extract_key(filename):
    # This is pretty similar to keyring.secret()...
    if os.path.exists(filename):
        with open(filename, 'r') as keyring:
            for line in keyring:
                if "key" in line and " = " in line:
                    return line.split(" = ")[1].strip()
    return ""

def inspect(**kwargs):
    # deliberately only looking for things ceph-deploy can deploy
    ceph_services = ['ceph-mon', 'ceph-osd', 'ceph-mds', 'ceph-radosgw']

    #
    # running_services will be something like:
    #
    # {
    #   'ceph-mon': [ 'hostname' ],
    #   'ceph-osd': [ '0', '1', '2', ... ]
    # }
    #
    running_services = {}
    for rs in __salt__['service.get_running']():
        instance = rs.split('@')
        if len(instance) == 2 and instance[0] in ceph_services:
            if not running_services.has_key(instance[0]):
                running_services[instance[0]] = []
            running_services[instance[0]].append(instance[1])

    ceph_keys = {}

    ceph_keys["ceph.client.admin"] = _extract_key("/etc/ceph/ceph.client.admin.keyring")
    ceph_keys["bootstrap-osd"] = _extract_key("/var/lib/ceph/bootstrap-osd/ceph.keyring")

    if "ceph-mon" in running_services.keys():
        ceph_keys["mon"] = _extract_key("/var/lib/ceph/mon/ceph-" + running_services["ceph-mon"][0] + "/keyring")

    # TODO: something similar to the above for MDS and RGW keys (but be aware
    # there might be multiple instances.  Hell, there could be multiple instances
    # for MONs too on one host, if someone has set up something really weird...

    # note that some keys will be empty strings if not present
    return {
        "running_services": running_services,
        "ceph_keys": ceph_keys
    }
