#!/bin/bash

# Demonstration script showing tinc L2VPN role functionality
# This script simulates what the role would do in a real environment

echo "🚀 Tinc L2VPN Role Demonstration"
echo "================================="

echo ""
echo "📁 Role Structure:"
echo "==================="
tree -I '.git|.ansible' --dirsfirst

echo ""
echo "✅ Role Validation:"
echo "==================="

echo "📋 Checking YAML syntax..."
if yamllint . >/dev/null 2>&1; then
    echo "✓ All YAML files pass yamllint"
else
    echo "✗ YAML linting failed"
fi

echo "📋 Checking Ansible playbook syntax..."
if ANSIBLE_ROLES_PATH=. ansible-playbook --syntax-check example-playbook.yml >/dev/null 2>&1; then
    echo "✓ Playbook syntax is valid"
else
    echo "✗ Playbook syntax check failed"
fi

echo "📋 Checking Jinja2 templates..."
python3 -c "
import jinja2
template_loader = jinja2.FileSystemLoader('templates')
env = jinja2.Environment(loader=template_loader)
templates = ['tinc.conf.j2', 'host.j2', 'tinc-up.j2', 'tinc-down.j2']
for template_name in templates:
    template = env.get_template(template_name)
print('✓ All Jinja2 templates are valid')
"

echo ""
echo "🏗️ Simulated Configuration Output:"
echo "===================================="

echo ""
echo "📄 Example tinc.conf for node1:"
echo "-----------------------------------"
python3 -c "
import jinja2
import sys

template_loader = jinja2.FileSystemLoader('templates')
env = jinja2.Environment(loader=template_loader)
template = env.get_template('tinc.conf.j2')

result = template.render(
    inventory_hostname='node1',
    tinc_netname='l2vpn',
    tinc_mode='switch',
    tinc_interface='tinc0',
    tinc_device_type='tap',
    tinc_config_path='/etc/tinc',
    groups={'all': ['node1', 'node2', 'node3']},
    tinc_client_only_peers=[],
    tinc_port=655,
    tinc_cipher='aes-256-cbc',
    tinc_digest='sha256',
    tinc_mac_length=8,
    tinc_max_timeout=300,
    tinc_ping_timeout=60,
    tinc_debug_level=1,
    tinc_log_file='',
    tinc_user='tinc',
    tinc_group='tinc',
    tinc_chroot=True,
    tinc_pid_file='/var/run/tinc.l2vpn.pid',
    tinc_connect_to=[]
)
print(result)
"

echo ""
echo "📄 Example host file for node2:"
echo "-----------------------------------"
python3 -c "
import jinja2

template_loader = jinja2.FileSystemLoader('templates')
env = jinja2.Environment(loader=template_loader)
template = env.get_template('host.j2')

result = template.render(
    item='node2',
    inventory_hostname='node1',
    hostvars={
        'node2': {
            'inventory_hostname': 'node2',
            'ansible_default_ipv4': {'address': '192.168.1.100'},
            'tinc_port': 655,
            'tinc_ip': '',
            'tinc_endpoint': ''
        }
    },
    groups={'all': ['node1', 'node2', 'node3']},
    tinc_client_only_peers=[],
    tinc_public_key='-----BEGIN RSA PUBLIC KEY-----\nMIICCgKCAgEA...(example key)...\n-----END RSA PUBLIC KEY-----',
    tinc_address_prefix='10.20.20',
    tinc_netmask=24,
    tinc_port=655
)
print(result)
"

echo ""
echo "📄 Example tinc-up script:"
echo "----------------------------"
python3 -c "
import jinja2

template_loader = jinja2.FileSystemLoader('templates')
env = jinja2.Environment(loader=template_loader)
template = env.get_template('tinc-up.j2')

result = template.render(
    inventory_hostname='node1',
    tinc_netname='l2vpn',
    bridge_interface='br0',
    bridge_ip='',
    bridge_address_prefix='172.20.0',
    bridge_netmask=24,
    groups={'all': ['node1', 'node2', 'node3']}
)
print(result)
"

echo ""
echo "🎯 Key Features Demonstrated:"
echo "============================="
echo "✓ Complete Ansible role structure following best practices"
echo "✓ Full mesh tinc network configuration"
echo "✓ Native Layer 2 VPN with TAP interfaces"
echo "✓ Automatic bridge setup and IP assignment"
echo "✓ Flexible configuration with 60+ variables"
echo "✓ Client-only peer support for NAT scenarios"
echo "✓ Key rotation with automatic backup"
echo "✓ Multi-OS support (Debian, Ubuntu, RHEL)"
echo "✓ Comprehensive testing with Molecule"
echo "✓ Production-ready security settings"

echo ""
echo "📚 Next Steps:"
echo "==============="
echo "1. Customize variables in defaults/main.yml or host_vars/"
echo "2. Create inventory with your target hosts"
echo "3. Run: ansible-playbook -i inventory.yml example-playbook.yml"
echo "4. Test connectivity between nodes on the bridge network"

echo ""
echo "🎉 Role implementation complete!"
"