# 🌐 Ansible Role: Tinc L2VPN

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Ansible Galaxy](https://img.shields.io/badge/Ansible%20Galaxy-cedricfarinazzo.tinc__l2vpn-blue)](https://galaxy.ansible.com/cedricfarinazzo/tinc_l2vpn)

> **An advanced Ansible role that creates a Layer 2 VPN using tinc mesh networking and Linux bridge interfaces.**

This role establishes a secure, scalable Layer 2 network overlay that allows distributed hosts to communicate as if they were on the same LAN segment, regardless of their physical network location. Unlike other VPN solutions, tinc provides native Layer 2 capabilities without the need for additional encapsulation protocols.

## 🚀 Quick Start

```yaml
# Simple inventory setup
- hosts: tinc_nodes
  roles:
    - cedricfarinazzo.tinc_l2vpn
```

**Important**: All hosts must be in the `tinc_nodes` inventory group for the full mesh topology to work correctly.

That's it! The role will automatically:
- ✅ Generate RSA key pairs for each host
- ✅ Create a full mesh VPN topology
- ✅ Configure native Layer 2 switching
- ✅ Set up bridge interfaces with static IPs
- ✅ Enable secure communication between all nodes

## 📋 Requirements

| Component | Requirement |
|-----------|-------------|
| **Operating System** | Linux with tinc package support |
| **Ansible** | Version 2.9+ |
| **Python** | Python 3.8+ on target hosts |
| **Network** | Internet connectivity for package installation |
| **Privileges** | Root or sudo access on target hosts |

### Supported Distributions

- ✅ **Debian** 11, 12
- ✅ **Ubuntu** 20.04, 22.04, 24.04
- ✅ **RHEL/CentOS** 8, 9

## ⚙️ Configuration

### Core Variables

The role uses sensible defaults but can be customized through these variables:

#### Tinc Configuration
```yaml
# Package and service management
tinc_package: tinc                     # Package name
tinc_package_state: present            # Package state
tinc_service_state: started            # Service state
tinc_service_enabled: true             # Enable on boot

# Network settings
tinc_netname: l2vpn                    # Network name
tinc_interface: tinc0                  # Interface name
tinc_mode: switch                      # Operating mode (switch/router)
tinc_port: 655                        # TCP/UDP port for tinc
tinc_device_type: tap                  # Device type (tap for L2)

# IP configuration
tinc_address_prefix: "10.20.20"       # IP prefix for mesh network
tinc_netmask: 24                       # Subnet mask

# IP address override (set in host_vars)
tinc_ip: ""                           # Override automatic IP assignment for specific hosts
                                      # Example: "10.20.20.50"
                                      # If empty, IP is auto-assigned based on host index

# Endpoint override (set in host_vars)
tinc_endpoint: ""                     # Override automatic endpoint assignment for specific hosts
                                      # Example: "example.com" or "1.2.3.4"
                                      # If empty, endpoint is auto-assigned using ansible_default_ipv4.address
```

#### Bridge Configuration
```yaml
bridge_interface: br0                  # Bridge interface name
bridge_address_prefix: "172.20.0"     # IP prefix for bridge network
bridge_netmask: 24                    # Bridge subnet mask

# Bridge IP address override (set in host_vars)
bridge_ip: ""                         # Override automatic bridge IP assignment for specific hosts
                                      # Example: "172.20.0.50"
                                      # If empty, IP is auto-assigned based on host index
```

#### Advanced Configuration
```yaml
# Connection management
tinc_connect_to: []                   # Explicit list of hosts to connect to (empty = connect to all)
tinc_client_only_peers: []            # List of hosts to exclude from address configuration

# Connection timeouts
tinc_max_timeout: 300                 # Maximum timeout for connections
tinc_ping_timeout: 60                 # Ping timeout

# Security settings
tinc_cipher: "aes-256-cbc"           # Encryption cipher
tinc_digest: "sha256"                # Hash algorithm
tinc_mac_length: 8                   # MAC length

# Key rotation settings
tinc_key_rotation_enabled: false     # Enable automatic key rotation
tinc_key_rotation_days: 365          # Rotate keys every X days

# Process settings
tinc_user: tinc                      # User to run tinc daemon
tinc_group: tinc                     # Group for tinc daemon
tinc_chroot: true                    # Enable chroot for security

# Logging
tinc_debug_level: 1                  # Debug level (0-5)
tinc_log_file: ""                    # Log file path (empty = syslog)
```

## 🏗️ Network Architecture

### Network Stack Components

| Layer | Component | Purpose | Configuration |
|-------|-----------|---------|---------------|
| **L2 Bridge** | `br0` | Provides Layer 2 switching | Static IPs: `172.20.0.x/24` |
| **Tinc TAP** | `tinc0` | Native L2 VPN interface | Switch mode, full mesh |
| **VPN Mesh** | `tinc daemon` | Secure mesh networking | Full mesh topology: `10.20.20.x/24` |
| **Physical** | `eth0` | Internet connectivity | DHCP/Static (existing) |

### Multi-Node Topology

```
    ┌──────────────────────┐     ┌──────────────────────┐     ┌──────────────────────┐
    │       Node A         │     │       Node B         │     │       Node C         │
    │                      │     │                      │     │                      │
    │  ┏━━━━━━━━━━━━━━━┓   │     │  ┏━━━━━━━━━━━━━━━┓   │     │  ┏━━━━━━━━━━━━━━━┓   │
    │  ┃ br0           ┃   │     │  ┃ br0           ┃   │     │  ┃ br0           ┃   │
    │  ┃ 172.20.0.11   ┃   │     │  ┃ 172.20.0.12   ┃   │     │  ┃ 172.20.0.13   ┃   │
    │  ┗━━━━━━┯━━━━━━━━┛   │     │  ┗━━━━━━┯━━━━━━━━┛   │     │  ┗━━━━━━┯━━━━━━━━┛   │
    │         │            │     │         │            │     │         │            │
    │  ┌──────┴──────┐     │     │  ┌──────┴──────┐     │     │  ┌──────┴──────┐     │
    │  │ tinc0       │     │     │  │ tinc0       │     │     │  │ tinc0       │     │
    │  │ TAP Device  │     │     │  │ TAP Device  │     │     │  │ TAP Device  │     │
    │  └──────┬──────┘     │     │  └──────┬──────┘     │     │  └──────┬──────┘     │
    │         │            │     │         │            │     │         │            │
    │  ┌──────┴──────┐     │     │  ┌──────┴──────┐     │     │  ┌──────┴──────┐     │
    │  │ tinc daemon │     │     │  │ tinc daemon │     │     │  │ tinc daemon │     │
    │  │ 10.20.20.1  │     │     │  │ 10.20.20.2  │     │     │  │ 10.20.20.3  │     │
    │  └──────┬──────┘     │     │  └──────┬──────┘     │     │  └──────┬──────┘     │
    └─────────┼────────────┘     └─────────┼────────────┘     └─────────┼────────────┘
              │                            │                            │
              └────────────────────────────┬────────────────────────────┘
                                           │
                                    ┌──────┴──────┐
                                    │   Internet  │
                                    │  (Encrypted │
                                    │   Tunnels)  │
                                    └─────────────┘
```

### Traffic Flow

1. **Application Traffic** → Bridge interface (`br0`)
2. **L2 Frames** → Tinc TAP interface (`tinc0`)  
3. **Encrypted Packets** → Internet routing via tinc daemon

## 🔧 How It Works

1. **Tinc Setup**: Automatic RSA key generation and full mesh configuration
2. **TAP Interface**: Creates native Layer 2 interface in switch mode
3. **Bridge Integration**: Linux bridge provides local L2 switching with static IPs
4. **Mesh Networking**: Each node connects to all other nodes automatically

## 📦 Dependencies

This role has **zero external dependencies** and uses only:
- ✅ **Ansible Core Modules** (built-in)
- ✅ **Linux Kernel Features** (TAP interfaces, Bridges)
- ✅ **Standard Packages** (available in all major distributions)

## 🎯 Usage Examples

### Basic Multi-Site Setup
```yaml
- hosts: tinc_nodes
  become: true
  roles:
    - role: cedricfarinazzo.tinc_l2vpn
      vars:
        bridge_address_prefix: "192.168.100"
```

### Client-Only Node Configuration
For hosts that are not accessible from the internet (e.g., behind NAT without port forwarding):
```yaml
- hosts: tinc_nodes
  become: true
  roles:
    - role: cedricfarinazzo.tinc_l2vpn

# Configuration on the server side:
# host_vars/server1.yml (publicly accessible server)
tinc_client_only_peers:
  - internal_node1
  - internal_node2

# host_vars/server2.yml (another publicly accessible server)
tinc_client_only_peers:
  - internal_node1
  - internal_node2
```
This configuration means:
- `server1` and `server2` **will NOT** have `Address` lines for `internal_node1` and `internal_node2`
- `internal_node1` and `internal_node2` **will** have `Address` lines for `server1` and `server2`
- All nodes will still be able to communicate through the mesh once connections are established

### Custom IP Addressing
```yaml
# host_vars/node1.yml
tinc_ip: "10.20.20.100"
bridge_ip: "172.20.0.100"

# host_vars/node2.yml
tinc_ip: "10.20.20.200"
bridge_ip: "172.20.0.200"
```

### High Security Configuration
```yaml
- hosts: tinc_nodes
  become: true
  roles:
    - role: cedricfarinazzo.tinc_l2vpn
      vars:
        tinc_cipher: "aes-256-gcm"
        tinc_digest: "sha512"
        tinc_key_rotation_enabled: true
        tinc_key_rotation_days: 90
        tinc_debug_level: 0
```

## 🔒 Security Considerations

### Key Management
- **Automatic Generation**: RSA keys are automatically generated if not provided
- **Key Rotation**: Keys can be rotated automatically with minimal downtime
- **Backup**: Old keys are backed up before rotation

### Network Security
- **Encryption**: All traffic encrypted with configurable ciphers
- **Authentication**: RSA key-based authentication prevents unauthorized access
- **Mesh Topology**: No single point of failure

### Process Security
- **User Isolation**: Runs as dedicated tinc user
- **Chroot**: Optional chroot jail for additional isolation
- **Privilege Dropping**: Drops privileges after initialization

## 🧪 Testing

### Quick Testing
```bash
# Run test against debian12
make test

# Test against all supported distributions
make molecule-test-all
```

### Test Coverage
- Package installation and service configuration
- Full mesh connectivity between all nodes
- Bridge interface validation
- Key generation and exchange
- Multi-distribution compatibility

## 📊 Comparison with WireGuard L2VPN

| Feature | Tinc L2VPN | WireGuard L2VPN |
|---------|------------|-----------------|
| **Layer 2 Support** | Native | Via VXLAN overlay |
| **Mesh Topology** | Native mesh | Star/hub topology |
| **Key Management** | RSA keys | Curve25519 keys |
| **Performance** | Good | Excellent |
| **Complexity** | Moderate | Simple |
| **NAT Traversal** | Automatic | Manual configuration |
| **Dynamic Routing** | Built-in | Requires additional setup |

## 🔍 Troubleshooting

### Common Issues

**Service won't start:**
```bash
# Check service status
systemctl status tinc@l2vpn

# Check configuration
tincd -n l2vpn -D -d3
```

**Connectivity issues:**
```bash
# Check interface status
ip link show tinc0
ip link show br0

# Check routing
ip route show

# Test direct tinc connectivity
telnet <peer-ip> 655
```

**Key issues:**
```bash
# Regenerate keys
rm /etc/tinc/l2vpn/rsa_key.*
echo "" | tincd -n l2vpn -K4096
```

## 👥 Authors & Contributors

**Cédric Farinazzo** ([@cedricfarinazzo](https://github.com/cedricfarinazzo)) - *Author and Maintainer*

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
