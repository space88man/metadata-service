import falcon
from jinja2 import Template
import json
import yaml

with open('database.yml') as dbase:
    config_db = yaml.load(dbase)

INSTANCES = config_db['instances']    

METADATA_JSON_J2 = '''{
  "uuid" : "{{ instance_id }}",
  "hostname": "{{ local_hostname }}",
  "name": "metadata-service",
  "network_config": { "content_path": "/content/0000" }
}'''

NETWORK_0000_J2 = '''auto {{ if_name }}
iface {{ if_name }} inet static
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

class Ec2MetaData:
    def on_get(self, req, resp, key):
        print("<7> Ec2MetaData", req.remote_addr, req.access_route, key)
        my_key = req.access_route[0]
        if my_key in INSTANCES:
            print("<7>", my_key, INSTANCES[my_key])
            key_0 = key.replace('-', '_')
            resp.body = INSTANCES[my_key].get(key_0, "")
        else:
            resp.status = HTTP_404

class Ec2MetaDataRoot:
    def on_get(self, req, resp):
        print("<7> Ec2MetaData", req.remote_addr, req.access_route)
        my_key = req.access_route[0]
        if my_key in INSTANCES:
            print("<7>", my_key, INSTANCES[my_key])
            resp.body = "instance-id\nlocal-hostname\n"
        else:
            resp.status = HTTP_404

def user_data_render(my_key):

    template = Template ( open( INSTANCES[my_key]['user_data_tmpl'] ).read() )
    return template.render(  INSTANCES[my_key] )

class UserData:
    def on_get(self, req, resp):
        """Handles GET requests"""
        print("<7> UserData", req.remote_addr, req.access_route)
        my_key = req.access_route[0]
        if my_key in INSTANCES:
            print("<7>", my_key, INSTANCES[my_key])
            resp.body = user_data_render(my_key)
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

class OpenStackRoot:
    def on_get(self, req, resp):
        print("<7> OpenStackRoot", req.remote_addr, req.access_route)
        my_key = req.access_route[0]
        if my_key in INSTANCES:
            print("<7>", my_key, INSTANCES[my_key])
            resp.body = "latest"
        else:
            resp.status = HTTP_404

class Version:
    def on_get(self, req, resp):
        """Handles GET requests"""
        print("<7> Version", req.remote_addr, req.access_route)
        resp.body = "v0.0.1 2017-07-17"

            
            
with open('user-data') as fi:
    USER_DATA =  fi.read()

api = falcon.API()
api.add_route('/openstack', OpenStackRoot())
api.add_route('/openstack/latest/meta_data.json', MetaData())
api.add_route('/openstack/latest/user_data', UserData())
api.add_route('/openstack/content/{filename}', ContentData())
api.add_route('/latest/meta-data', NullData())

api.add_route('/2009-04-04/meta-data', Ec2MetaDataRoot())
api.add_route('/2009-04-04/meta-data/{key}', Ec2MetaData())
api.add_route('/2009-04-04/user-data', UserData())
api.add_route('/api/v1/version', Version())
