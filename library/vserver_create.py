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
module: vserver_create
version_added: "1.0"
author: "Jeorry Balasabas (@jeorryb)"
short_description: Create vservers
description:
  - Ansible module to create a vservers on NetApp CDOT arrays via the NetApp python SDK.
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
  comment:
    required: False
    description:
      - "Comment associated with vserver if needed"
  ipspace:
    required: False
    description:
      - "IPSpace name; default is <Default>""
  language:
    required: False
    description:
      - "Language to use for vserver; default is C.UTF-8"
  root_vol:
    required: True
    description:
      - "Name of root volume for vserver"
  root_vol_aggr:
    required: True
    description:
      - "Aggr on which root volume will be created"
  security:
    required: True
    description:
      - "Security style of vserver root volume"
  vserver_sub:
    required: False
    description:
      - "Vserver subtype; choices are default|dp_destination|sync_source "


'''

EXAMPLES = '''
# Create vserver 
- name: Create svm_cifs
    vserver_create:
      cluster: "192.168.0.1"
      user_name: "admin"
      password: "Password1"
      vserver: "svm_cifs"
      root_vol: "svm_cifs_root"
      root_vol_aggr: "n01_aggr0"
      security: "ntfs"

'''

def vserver_create(module):

  cluster = module.params['cluster']
  user_name = module.params['user_name']
  password = module.params['password']
  vserver = module.params['vserver']
  comment = module.params['comment']
  ipspace = module.params['ipspace']
  language = module.params['language']
  root_vol = module.params['root_vol']
  root_vol_aggr = module.params['root_vol_aggr']
  security = module.params['security']
  vserver_sub = module.params['vserver_sub']

  results = {}

  results['changed'] = False

  s = NaServer(cluster, 1 , 0)
  s.set_server_type("FILER")
  s.set_transport_type("HTTPS")
  s.set_port(443)
  s.set_style("LOGIN")
  s.set_admin_user(user_name, password)

  api = NaElement('vserver-create')
  api.child_add_string('comment', comment)
  api.child_add_string('ipspace', ipspace)
  api.child_add_string('language', language)
  api.child_add_string('vserver-name', vserver)
  api.child_add_string('root-volume', root_vol)
  api.child_add_string('root-volume-aggregate', root_vol_aggr)
  api.child_add_string('root-volume-security-style', security)
  api.child_add_string('vserver-subtype', vserver_sub)
  

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
      comment=dict(required=False),
      vserver=dict(required=True),
      ipspace=dict(default='Default'),
      language=dict(default='C.UTF-8'),
      root_vol=dict(required=True),
      root_vol_aggr=dict(required=True),
      security=dict(required=True, choices=['unix', 'ntfs', 'mixed']),
      vserver_sub=dict(default='default', choices=['default', 'dp_destination', 'sync_source']),

    ),
    supports_check_mode = False
  )

  results = vserver_create(module)

  

  module.exit_json(**results)

from ansible.module_utils.basic import *
main()




