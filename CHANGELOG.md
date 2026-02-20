# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.0.0] - 2025-07-29

### Added

- Initial commit with base repository structure
- Complete tinc L2VPN Ansible role for full mesh network setup
- Molecule tests: verify connectivity with ping and side effect playbook

### Fixed

- Tinc hostname and tinc.conf configuration
- Verify playbook for molecule tests
- Key rotation handling

### Changed

- Updated README.md with role documentation

[Unreleased]: https://github.com/cedricfarinazzo/ansible-role-tinc-l2vpn/compare/1.0.0...HEAD
[1.0.0]: https://github.com/cedricfarinazzo/ansible-role-tinc-l2vpn/releases/tag/1.0.0
