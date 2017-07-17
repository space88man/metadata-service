import falcon
from jinja2 import Template
import json

INSTANCES = {
    '192.168.125.200': { 'instance_id': 'iid-e08cd154ca7a9491',
                         'local_hostname': 'cloud-9491',
                         'ip_address': '192.168.125.200'
    },
    '192.168.125.201': { 'instance_id': 'iid-95a39c8bdca53915',
                         'local_hostname': 'cloud-3915',
                         'ip_address': '192.168.125.201'
    }
}

METADATA_JSON_J2 = '''{
  "uuid" : "{{ instance_id }}",
  "hostname": "{{ local_hostname }}",
  "name": "metadata-service",
  "network_config": { "content_path": "/content/0000" }
}'''

NETWORK_0000_J2 = '''auto eth0
iface eth0 inet static
    address {{ ip_address }}
    network 192.168.125.0
    netmask 255.255.255.0
    broadcast 192.168.125.255
    gateway 192.168.125.1
    dns-nameservers 192.168.125.1

'''

METADATA_TMPL = Template(METADATA_JSON_J2)
NETWORK_TMPL = Template(NETWORK_0000_J2)

FILES = {"0000": NETWORK_TMPL,}


class MetaData:
    def on_get(self, req, resp):
        """Handles GET requests"""
        print("<7> MetaData", req.remote_addr, req.access_route)
        my_key = req.access_route[0]
        if my_key in INSTANCES:
            print("<7>", my_key, INSTANCES[my_key])
            resp.body = METADATA_TMPL.render(INSTANCES[my_key])
            resp.append_header('Content-Type', 'application/json')
        else:
            resp.status = HTTP_404

class UserData:
    def on_get(self, req, resp):
        """Handles GET requests"""
        print("<7> UserData", req.remote_addr, req.access_route)
        my_key = req.access_route[0]
        if my_key in INSTANCES:
            print("<7>", my_key, INSTANCES[my_key])
            user_data = USER_DATA
            resp.body = user_data
        else:
            resp.status = HTTP_404

class ContentData:
    def on_get(self, req, resp, filename):
        """Handles GET requests"""
        print("<7> ContentData", req.remote_addr, req.access_route)
        my_key = req.access_route[0]
        if my_key in INSTANCES:
            print("<7>", my_key, INSTANCES[my_key])
            if filename in FILES:
                resp.body = FILES[filename].render(INSTANCES[my_key])
        else:
            resp.status = HTTP_404

class NullData:
    def on_get(self, req, resp):
        """Handles GET requests"""
        print("<7> NullData", req.remote_addr, req.access_route)
        my_key = req.access_route[0]
        if my_key in INSTANCES:
            print("<7>", my_key, INSTANCES[my_key])
        else:
            resp.status = HTTP_404

            
            
with open('user-data') as fi:
    USER_DATA =  fi.read()

api = falcon.API()
api.add_route('/openstack/latest/meta_data.json', MetaData())
api.add_route('/openstack/latest/user_data', UserData())
api.add_route('/openstack/content/{filename}', ContentData())
api.add_route('/latest/meta-data', NullData())
