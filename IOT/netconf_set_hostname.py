from ncclient import manager

ROUTER_IP = "10.0.137.231"
USERNAME = "admin"
PASSWORD = "Admin123!"

hostname_config = """
<config>
  <native xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-native">
    <hostname>Router-Python</hostname>
  </native>
</config>
"""

with manager.connect(
    host=ROUTER_IP,
    port=830,
    username=USERNAME,
    password=PASSWORD,
    hostkey_verify=False,
    allow_agent=False,
    look_for_keys=False,
    timeout=30
) as m:
    reply = m.edit_config(target="running", config=hostname_config)
    print(reply)
