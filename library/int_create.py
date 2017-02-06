#!/usr/bin/python

import sys
import json

try:
  from NaServer import *
  NASERVER_AVAILABLE = True
except ImportError:
  NASERVER_AVAILABLE = False

if not NASERVER_AVAILABLE:
    module.fail_json(msg="The NetApp Manageability SDK library is not installed")

DOCUMENTATTION = '''
---
module: lif_create
version_added: "1.0"
author: "Jeorry Balasabas (@jeorryb)"
short_description: Create interface
description:
  - Ansible module to create interfaces on NetApp CDOT arrays via the NetApp python SDK.
requirements:
  - NetApp Manageability SDK
options:
  cluster:
    required: True
    description:
      - "The ip address or hostname of the cluster"
  user_name:
    required: True
    description:
      - "Administrator user for the cluster/node"
  password:
    required: True
    description:
      - "password for the admin user"
  vserver:
    required: True
    description:
      - "vserver name"
  lif:
    required: True
    description:
      - "name of the logical interface"
  role:
    required: True
    description:
      - "specifies the role of the LIF"
  data_proto:
    required: False
    description:
      - "Specifies the list of data protocols specified on the LIF"
  node:
    required: True
    description:
      - "Home node of the LIF"
  port:
    required: True
    description:
      - "Home port of the LIF"
  ip:
    required: True
    description:
      - "IP address of the LIF"
  netmask:
    required: True
    description:
      - "Subnet mask of the LIF"
  subnet:
    required: False
    description:
      - "subnet name; ip and netmask not used if this parameter is specified"


'''

EXAMPLES = '''
# Create lif lif_nfs_01
- name: Create lif for nfs
    int_create:
      cluster: "192.168.0.1"
      user_name: "admin"
      password: "Password1"
      vserver: "svm_nfs"
      lif: "lif_nfs_01"
      role: "data"
      data_proto: "nfs"
      node: "atlcdot-01"
      port: "e0d"
      ip: "192.168.1.178"
      netmask: "255.255.255.0"

'''

def int_create(module):

  cluster = module.params['cluster']
  user_name = module.params['user_name']
  password = module.params['password']
  node = module.params['node']
  vserver = module.params['vserver']
  lif = module.params['lif']
  role = module.params['role']
  data_proto = module.params['data_proto']
  port = module.params['port']
  ip = module.params['ip']
  netmask = module.params['netmask']
  subnet = module.params['subnet']

  results = {}

  results['changed'] = False

  s = NaServer(cluster, 1 , 0)
  s.set_server_type("FILER")
  s.set_transport_type("HTTPS")
  s.set_port(443)
  s.set_style("LOGIN")
  s.set_admin_user(user_name, password)

  api = NaElement('net-interface-create')
  api.child_add_string('address', ip)

  xi = NaElement('data-protocols')
  api.child_add(xi)

  for proto in data_proto:
    xi.child_add_string('data-protocol', proto)

  api.child_add_string('home-node', node)
  api.child_add_string('home-port', port)
  api.child_add_string('interface-name', lif)
  api.child_add_string('netmask', netmask)
  api.child_add_string('role', role)
  api.child_add_string('vserver', vserver)
  if module.params['subnet']:
    api.child_add_string('subnet-name', subnet)




  xo = s.invoke_elem(api)

  if(xo.results_errno() != 0):
    r = xo.results_reason()
    module.fail_json(msg=r)
    results['changed'] = False

  else:
    results['changed'] = True

  return results

def main():
  module = AnsibleModule(
    argument_spec = dict(
      cluster=dict(required=True),
      user_name=dict(required=True),
      password=dict(required=True),
      node=dict(required=True),
      vserver=dict(required=True),
      lif=dict(required=True),
      role=dict(default='data', choices=['undef', 'cluster', 'data', 'node_mgmt', 'intercluster', 'cluster_mgmt']),
      data_proto=dict(required=False, type='list'),
      port=dict(required=True),
      ip=dict(required=True),
      netmask=dict(required=True),
      subnet=dict(required=False),

    ),
    supports_check_mode = False
  )

  results = int_create(module)



  module.exit_json(**results)

from ansible.module_utils.basic import *
main()
