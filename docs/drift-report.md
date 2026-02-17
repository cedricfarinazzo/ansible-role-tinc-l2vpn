# Documentation Drift Report

Generated for ansible-role-tinc-l2vpn

## Summary

- **Mismatched values**: 9
- **Undocumented variables**: 4
- **Non-existent documented variables**: 1

## ⚠️ Mismatched Values

Variables where README documentation differs from actual defaults:

| Variable | README Value | Actual Default |
|----------|--------------|----------------|
| `tinc_hostname` | `hub` | `` |
| `tinc_ip` | `10.20.20.200` | `` |
| `bridge_address_prefix` | `192.168.100` | `172.20.0` |
| `bridge_ip` | `172.20.0.200` | `` |
| `tinc_cipher` | `aes-256-gcm` | `aes-256-cbc` |
| `tinc_digest` | `sha512` | `sha256` |
| `tinc_key_rotation_enabled` | `true` | `false` |
| `tinc_key_rotation_days` | `90` | `30` |
| `tinc_debug_level` | `0` | `1` |

## 📝 Undocumented Variables

Variables defined in defaults/main.yml but not documented in README:

- `tinc_config_path`: `/etc/tinc`
- `tinc_networks_file`: `/etc/tinc/nets.boot`
- `tinc_pid_file`: `/var/run/tinc.{{ tinc_netname }}.pid`
- `tinc_systemd_path`: `/etc/systemd/system`

## ❌ Non-Existent Documented Variables

Variables documented in README but not defined in defaults/main.yml:

- `become`: `true` (documented)
