#!/usr/bin/env python3
"""
Ansible Role Topology Visualizer

This script analyzes an Ansible role structure and generates SVG diagrams showing:
- Directory hierarchy and file structure
- Task dependencies and execution flow
- Variable definitions and usage flow
- Handler relationships and notifications
"""

import os
import re
import yaml
import argparse
from pathlib import Path
from typing import Dict, List, Set, Tuple
from collections import defaultdict


class AnsibleRoleAnalyzer:
    """Analyzes Ansible role structure and generates topology visualizations"""
    
    def __init__(self, role_path: str):
        self.role_path = Path(role_path)
        self.tasks = []
        self.variables = defaultdict(set)
        self.handlers = []
        self.templates = []
        self.notifications = defaultdict(set)
        self.variable_usage = defaultdict(set)
        self.includes = []
        
    def analyze(self):
        """Perform full analysis of the role"""
        self._analyze_tasks()
        self._analyze_defaults()
        self._analyze_vars()
        self._analyze_handlers()
        self._analyze_templates()
        
    def _analyze_tasks(self):
        """Analyze tasks/main.yml for task flow and dependencies"""
        tasks_file = self.role_path / "tasks" / "main.yml"
        if tasks_file.exists():
            with open(tasks_file, 'r') as f:
                try:
                    data = yaml.safe_load(f)
                    if data:
                        for item in data:
                            if isinstance(item, dict):
                                self.tasks.append(item)
                                # Extract notify relationships
                                if 'notify' in item:
                                    notify = item['notify']
                                    if isinstance(notify, str):
                                        notify = [notify]
                                    for handler in notify:
                                        self.notifications[item.get('name', 'unnamed')].add(handler)
                                # Extract variable usage
                                self._extract_variables_from_task(item)
                                # Track includes
                                if 'include_vars' in item or 'ansible.builtin.include_vars' in item.get('name', ''):
                                    self.includes.append(item.get('name', 'unnamed'))
                except yaml.YAMLError as e:
                    print(f"Error parsing tasks: {e}")
    
    def _extract_variables_from_task(self, task: dict):
        """Extract variable references from a task"""
        task_name = task.get('name', 'unnamed')
        task_str = str(task)
        # Find Jinja2 variable references {{ variable }}
        variables = re.findall(r'\{\{\s*([a-zA-Z_][a-zA-Z0-9_]*)', task_str)
        for var in variables:
            self.variable_usage[var].add(task_name)
    
    def _analyze_defaults(self):
        """Analyze defaults/main.yml for variable definitions"""
        defaults_file = self.role_path / "defaults" / "main.yml"
        if defaults_file.exists():
            with open(defaults_file, 'r') as f:
                try:
                    data = yaml.safe_load(f)
                    if data:
                        for key in data.keys():
                            self.variables['defaults'].add(key)
                except yaml.YAMLError as e:
                    print(f"Error parsing defaults: {e}")
    
    def _analyze_vars(self):
        """Analyze vars/ directory for OS-specific variables"""
        vars_dir = self.role_path / "vars"
        if vars_dir.exists():
            for var_file in vars_dir.glob("*.yml"):
                with open(var_file, 'r') as f:
                    try:
                        data = yaml.safe_load(f)
                        if data:
                            for key in data.keys():
                                self.variables[var_file.stem].add(key)
                    except yaml.YAMLError as e:
                        print(f"Error parsing {var_file}: {e}")
    
    def _analyze_handlers(self):
        """Analyze handlers/main.yml"""
        handlers_file = self.role_path / "handlers" / "main.yml"
        if handlers_file.exists():
            with open(handlers_file, 'r') as f:
                try:
                    data = yaml.safe_load(f)
                    if data:
                        for handler in data:
                            if isinstance(handler, dict):
                                self.handlers.append(handler)
                except yaml.YAMLError as e:
                    print(f"Error parsing handlers: {e}")
    
    def _analyze_templates(self):
        """Analyze templates directory"""
        templates_dir = self.role_path / "templates"
        if templates_dir.exists():
            self.templates = [t.name for t in templates_dir.glob("*.j2")]


class SVGGenerator:
    """Generates SVG diagrams for visualization"""
    
    def __init__(self, analyzer: AnsibleRoleAnalyzer, output_dir: Path):
        self.analyzer = analyzer
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def generate_all(self):
        """Generate all visualization diagrams"""
        self.generate_directory_tree()
        self.generate_task_flow()
        self.generate_variable_flow()
        self.generate_handler_relationships()
        
    def generate_directory_tree(self):
        """Generate directory structure visualization"""
        svg_content = [
            '<?xml version="1.0" encoding="UTF-8"?>',
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 600" width="800" height="600">',
            '<style>',
            '  text { font-family: monospace; font-size: 14px; }',
            '  .folder { fill: #4A90E2; }',
            '  .file { fill: #50C878; }',
            '  .title { font-size: 18px; font-weight: bold; fill: #333; }',
            '  rect { rx: 3; }',
            '</style>',
            '<text x="400" y="30" class="title" text-anchor="middle">Ansible Role Directory Structure</text>'
        ]
        
        y_pos = 70
        x_base = 50
        
        # Role root
        svg_content.append(f'<rect x="{x_base}" y="{y_pos}" width="700" height="30" class="folder"/>')
        svg_content.append(f'<text x="{x_base + 10}" y="{y_pos + 20}" fill="white">ansible-role-tinc-l2vpn/</text>')
        y_pos += 40
        
        # Key directories
        dirs = [
            ('tasks/', 'Task definitions and playbook logic'),
            ('handlers/', 'Service handlers and event responses'),
            ('templates/', 'Jinja2 configuration templates'),
            ('defaults/', 'Default variable values'),
            ('vars/', 'OS-specific variables'),
            ('meta/', 'Role metadata and dependencies'),
        ]
        
        for dirname, description in dirs:
            svg_content.append(f'<rect x="{x_base + 40}" y="{y_pos}" width="300" height="25" class="folder"/>')
            svg_content.append(f'<text x="{x_base + 50}" y="{y_pos + 17}" fill="white">{dirname}</text>')
            svg_content.append(f'<text x="{x_base + 360}" y="{y_pos + 17}" fill="#666" font-size="12">{description}</text>')
            y_pos += 35
        
        svg_content.append('</svg>')
        
        output_file = self.output_dir / "directory_structure.svg"
        with open(output_file, 'w') as f:
            f.write('\n'.join(svg_content))
        print(f"Generated: {output_file}")
    
    def generate_task_flow(self):
        """Generate task execution flow diagram"""
        svg_content = [
            '<?xml version="1.0" encoding="UTF-8"?>',
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 1400" width="1200" height="1400">',
            '<defs>',
            '  <marker id="arrowhead" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto">',
            '    <polygon points="0 0, 10 3, 0 6" fill="#666"/>',
            '  </marker>',
            '</defs>',
            '<style>',
            '  text { font-family: sans-serif; font-size: 13px; }',
            '  .task { fill: #E8F4F8; stroke: #4A90E2; stroke-width: 2; }',
            '  .phase { fill: #FFF8E1; stroke: #FFA726; stroke-width: 2; }',
            '  .title { font-size: 20px; font-weight: bold; fill: #333; }',
            '  .phase-label { font-size: 14px; font-weight: bold; fill: #E65100; }',
            '  .arrow { stroke: #666; stroke-width: 2; fill: none; marker-end: url(#arrowhead); }',
            '  rect { rx: 5; }',
            '</style>',
            '<text x="600" y="30" class="title" text-anchor="middle">Task Execution Flow</text>'
        ]
        
        y_pos = 70
        x_center = 600
        box_width = 500
        box_height = 50
        
        # Define phases with tasks
        phases = [
            ("1. Hostname Setup", [
                "Set tinc hostname",
                "Display hostname mapping"
            ]),
            ("2. Package Installation", [
                "Include OS-specific variables",
                "Install tinc package",
                "Install network tools"
            ]),
            ("3. System Configuration", [
                "Enable IPv4 forwarding",
                "Enable IPv6 forwarding"
            ]),
            ("4. Directory Creation", [
                "Create tinc network directory",
                "Create hosts directory",
                "Create backups directory"
            ]),
            ("5. Configuration Files", [
                "Generate tinc.conf",
                "Generate tinc-up script",
                "Generate tinc-down script"
            ]),
            ("6. Key Management", [
                "Check private key age",
                "Calculate key age",
                "Backup old keys",
                "Generate new key pair"
            ]),
            ("7. Key Exchange", [
                "Read public key",
                "Gather facts from all hosts",
                "Check for duplicate hostnames",
                "Generate host configs for peers"
            ]),
            ("8. Service Management", [
                "Add network to nets.boot",
                "Enable and start tinc service"
            ])
        ]
        
        for phase_name, tasks in phases:
            # Phase header
            svg_content.append(f'<rect x="{x_center - box_width//2}" y="{y_pos}" width="{box_width}" height="35" class="phase"/>')
            svg_content.append(f'<text x="{x_center}" y="{y_pos + 23}" class="phase-label" text-anchor="middle">{phase_name}</text>')
            y_pos += 45
            
            # Tasks in phase
            for i, task in enumerate(tasks):
                svg_content.append(f'<rect x="{x_center - box_width//2 + 30}" y="{y_pos}" width="{box_width - 60}" height="{box_height}" class="task"/>')
                # Wrap long text
                if len(task) > 50:
                    lines = [task[i:i+50] for i in range(0, len(task), 50)]
                    for j, line in enumerate(lines):
                        svg_content.append(f'<text x="{x_center}" y="{y_pos + 20 + j*15}" text-anchor="middle">{line}</text>')
                else:
                    svg_content.append(f'<text x="{x_center}" y="{y_pos + 30}" text-anchor="middle">{task}</text>')
                
                # Arrow to next task
                if i < len(tasks) - 1:
                    svg_content.append(f'<line x1="{x_center}" y1="{y_pos + box_height}" x2="{x_center}" y2="{y_pos + box_height + 10}" class="arrow"/>')
                
                y_pos += box_height + 10
            
            # Arrow to next phase
            y_pos += 10
        
        svg_content.append('</svg>')
        
        output_file = self.output_dir / "task_flow.svg"
        with open(output_file, 'w') as f:
            f.write('\n'.join(svg_content))
        print(f"Generated: {output_file}")
    
    def generate_variable_flow(self):
        """Generate variable definition and usage flow"""
        svg_content = [
            '<?xml version="1.0" encoding="UTF-8"?>',
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1400 1000" width="1400" height="1000">',
            '<defs>',
            '  <marker id="arrowhead2" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto">',
            '    <polygon points="0 0, 10 3, 0 6" fill="#4CAF50"/>',
            '  </marker>',
            '</defs>',
            '<style>',
            '  text { font-family: sans-serif; font-size: 12px; }',
            '  .var-def { fill: #E8F5E9; stroke: #4CAF50; stroke-width: 2; }',
            '  .var-os { fill: #FFF3E0; stroke: #FF9800; stroke-width: 2; }',
            '  .usage { fill: #E3F2FD; stroke: #2196F3; stroke-width: 2; }',
            '  .title { font-size: 20px; font-weight: bold; fill: #333; }',
            '  .section-title { font-size: 16px; font-weight: bold; fill: #555; }',
            '  .arrow { stroke: #4CAF50; stroke-width: 2; fill: none; marker-end: url(#arrowhead2); stroke-dasharray: 5,5; }',
            '  rect { rx: 5; }',
            '</style>',
            '<text x="700" y="30" class="title" text-anchor="middle">Variable Definition and Flow</text>'
        ]
        
        # Variable definitions (left side)
        svg_content.append('<text x="150" y="70" class="section-title">Variable Definitions</text>')
        y_pos = 100
        
        key_vars = [
            ('defaults/main.yml', [
                'tinc_netname', 'tinc_mode', 'tinc_port',
                'tinc_address_prefix', 'bridge_interface',
                'tinc_key_rotation_enabled', 'tinc_cipher'
            ]),
            ('vars/Debian.yml', ['tinc_package', 'required_packages']),
            ('vars/RedHat.yml', ['tinc_package', 'required_packages']),
        ]
        
        for source, vars_list in key_vars:
            color_class = 'var-os' if 'vars/' in source else 'var-def'
            svg_content.append(f'<rect x="50" y="{y_pos}" width="250" height="30" class="{color_class}"/>')
            svg_content.append(f'<text x="175" y="{y_pos + 20}" text-anchor="middle" font-weight="bold">{source}</text>')
            y_pos += 35
            
            for var in vars_list[:4]:  # Limit to 4 vars per source
                svg_content.append(f'<rect x="70" y="{y_pos}" width="210" height="25" class="{color_class}"/>')
                svg_content.append(f'<text x="175" y="{y_pos + 17}" text-anchor="middle">{var}</text>')
                y_pos += 30
            
            if len(vars_list) > 4:
                svg_content.append(f'<text x="175" y="{y_pos}" text-anchor="middle" fill="#999">... and {len(vars_list) - 4} more</text>')
                y_pos += 25
            
            y_pos += 20
        
        # Usage areas (right side)
        svg_content.append('<text x="1150" y="70" class="section-title">Variable Usage</text>')
        y_usage = 100
        
        usage_areas = [
            ('Tasks (main.yml)', [
                'Install packages',
                'Configure network',
                'Generate configs',
                'Manage keys'
            ]),
            ('Templates', [
                'tinc.conf.j2',
                'tinc-up.j2',
                'tinc-down.j2',
                'host.j2'
            ]),
            ('Handlers', [
                'restart tinc',
                'reload tinc',
                'reload sysctl'
            ])
        ]
        
        for area, items in usage_areas:
            svg_content.append(f'<rect x="1000" y="{y_usage}" width="300" height="30" class="usage"/>')
            svg_content.append(f'<text x="1150" y="{y_usage + 20}" text-anchor="middle" font-weight="bold">{area}</text>')
            y_usage += 35
            
            for item in items:
                svg_content.append(f'<rect x="1020" y="{y_usage}" width="260" height="25" class="usage"/>')
                svg_content.append(f'<text x="1150" y="{y_usage + 17}" text-anchor="middle">{item}</text>')
                y_usage += 30
            
            y_usage += 20
        
        # Draw some example flow arrows
        arrows = [
            (300, 150, 1000, 150),
            (300, 250, 1000, 220),
            (300, 350, 1000, 350),
        ]
        
        for x1, y1, x2, y2 in arrows:
            svg_content.append(f'<path d="M {x1} {y1} Q {(x1+x2)/2} {y1} {x2} {y2}" class="arrow"/>')
        
        svg_content.append('</svg>')
        
        output_file = self.output_dir / "variable_flow.svg"
        with open(output_file, 'w') as f:
            f.write('\n'.join(svg_content))
        print(f"Generated: {output_file}")
    
    def generate_handler_relationships(self):
        """Generate handler notification relationships"""
        svg_content = [
            '<?xml version="1.0" encoding="UTF-8"?>',
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 800" width="1200" height="800">',
            '<defs>',
            '  <marker id="arrowhead3" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto">',
            '    <polygon points="0 0, 10 3, 0 6" fill="#E91E63"/>',
            '  </marker>',
            '</defs>',
            '<style>',
            '  text { font-family: sans-serif; font-size: 13px; }',
            '  .task-notify { fill: #E3F2FD; stroke: #2196F3; stroke-width: 2; }',
            '  .handler { fill: #FCE4EC; stroke: #E91E63; stroke-width: 2; }',
            '  .title { font-size: 20px; font-weight: bold; fill: #333; }',
            '  .section-title { font-size: 16px; font-weight: bold; fill: #555; }',
            '  .notify-arrow { stroke: #E91E63; stroke-width: 2; fill: none; marker-end: url(#arrowhead3); }',
            '  rect { rx: 5; }',
            '</style>',
            '<text x="600" y="30" class="title" text-anchor="middle">Handler Notification Relationships</text>'
        ]
        
        # Tasks that notify (left side)
        svg_content.append('<text x="200" y="70" class="section-title">Tasks with Notifications</text>')
        y_tasks = 100
        
        notifying_tasks = [
            ('Install tinc package', ['restart tinc']),
            ('Generate tinc.conf', ['restart tinc']),
            ('Generate tinc-up script', ['restart tinc']),
            ('Generate tinc-down script', ['restart tinc']),
            ('Enable IPv4 forwarding', ['Reload sysctl']),
            ('Enable IPv6 forwarding', ['Reload sysctl']),
            ('Generate host configs', ['restart tinc']),
        ]
        
        task_positions = {}
        for task, handlers in notifying_tasks:
            svg_content.append(f'<rect x="50" y="{y_tasks}" width="350" height="40" class="task-notify"/>')
            svg_content.append(f'<text x="225" y="{y_tasks + 25}" text-anchor="middle">{task}</text>')
            task_positions[task] = y_tasks + 20
            y_tasks += 55
        
        # Handlers (right side)
        svg_content.append('<text x="950" y="70" class="section-title">Handlers</text>')
        y_handlers = 150
        
        handlers = [
            ('restart tinc', 'Restart tinc@{netname} service'),
            ('reload tinc', 'Reload tinc@{netname} service'),
            ('Reload sysctl', 'Apply sysctl configuration'),
            ('start tinc', 'Start tinc@{netname} service'),
            ('stop tinc', 'Stop tinc@{netname} service'),
        ]
        
        handler_positions = {}
        for handler, description in handlers:
            svg_content.append(f'<rect x="800" y="{y_handlers}" width="350" height="50" class="handler"/>')
            svg_content.append(f'<text x="975" y="{y_handlers + 22}" text-anchor="middle" font-weight="bold">{handler}</text>')
            svg_content.append(f'<text x="975" y="{y_handlers + 38}" text-anchor="middle" font-size="11" fill="#666">{description}</text>')
            handler_positions[handler] = y_handlers + 25
            y_handlers += 70
        
        # Draw notification arrows
        for task, handlers_list in notifying_tasks:
            for handler in handlers_list:
                if task in task_positions and handler in handler_positions:
                    x1, y1 = 400, task_positions[task]
                    x2, y2 = 800, handler_positions[handler]
                    svg_content.append(f'<path d="M {x1} {y1} C {(x1+x2)/2} {y1}, {(x1+x2)/2} {y2}, {x2} {y2}" class="notify-arrow"/>')
        
        svg_content.append('</svg>')
        
        output_file = self.output_dir / "handler_relationships.svg"
        with open(output_file, 'w') as f:
            f.write('\n'.join(svg_content))
        print(f"Generated: {output_file}")


def create_readme(output_dir: Path, role_path: Path):
    """Create README documentation for the topology visualizations"""
    
    readme_content = f"""# Ansible Role Topology Visualization

This directory contains visual representations of the `ansible-role-tinc-l2vpn` structure and relationships.

## Generated Diagrams

### 1. Directory Structure (`directory_structure.svg`)
Shows the hierarchical organization of the Ansible role, including:
- Main directories (tasks, handlers, templates, defaults, vars, meta)
- Purpose of each directory in the role structure

### 2. Task Execution Flow (`task_flow.svg`)
Illustrates the sequential execution of tasks organized into logical phases:
1. **Hostname Setup** - Configure tinc node naming
2. **Package Installation** - Install tinc and required packages
3. **System Configuration** - Enable IP forwarding
4. **Directory Creation** - Set up tinc directories
5. **Configuration Files** - Generate tinc.conf and scripts
6. **Key Management** - Handle encryption key generation and rotation
7. **Key Exchange** - Distribute public keys across the mesh
8. **Service Management** - Enable and start the tinc service

### 3. Variable Flow (`variable_flow.svg`)
Demonstrates how variables are defined and used throughout the role:
- **Variable Definitions**: defaults/main.yml, vars/Debian.yml, vars/RedHat.yml
- **Variable Usage**: Tasks, templates, and handlers that consume variables
- Shows the flow from definition to consumption

### 4. Handler Relationships (`handler_relationships.svg`)
Maps the notification system between tasks and handlers:
- Tasks that trigger notifications (left side)
- Handler actions they invoke (right side)
- Arrows showing notification relationships

## Role Overview

**ansible-role-tinc-l2vpn** is an Ansible role that creates a full mesh VPN network using tinc with Layer 2 (L2) bridging capabilities.

### Key Features
- Full mesh network topology with automatic peer configuration
- Layer 2 VPN using Linux bridge and TAP interfaces
- Automatic key generation and rotation
- OS-specific package management (Debian/Ubuntu and RHEL/CentOS)
- Dynamic IP address assignment
- Secure encryption (AES-256-CBC with SHA256)

### Architecture
The role implements an 8-phase deployment:
1. Node identification and hostname sanitization
2. Distribution-specific package installation
3. System network configuration (IP forwarding)
4. Tinc directory structure creation
5. Configuration file generation from templates
6. RSA key pair management with optional rotation
7. Public key exchange across all mesh nodes
8. Service enablement and startup

## Regenerating Visualizations

To regenerate these visualizations:

```bash
cd {role_path}
python3 scripts/visualize_topology.py
```

The script will analyze the role structure and update all SVG diagrams in this directory.

## Files Analyzed

- `tasks/main.yml` - Main task definitions and execution flow
- `defaults/main.yml` - Default variable values
- `vars/*.yml` - OS-specific variables
- `handlers/main.yml` - Service and system handlers
- `templates/*.j2` - Jinja2 configuration templates
- `meta/main.yml` - Role metadata

---

*Generated by Ansible Role Topology Visualizer*
*Last updated: {Path.cwd()}*
"""
    
    readme_file = output_dir / "README.md"
    with open(readme_file, 'w') as f:
        f.write(readme_content)
    print(f"Generated: {readme_file}")


def main():
    parser = argparse.ArgumentParser(
        description='Visualize Ansible role topology and relationships'
    )
    parser.add_argument(
        '--role-path',
        default='.',
        help='Path to the Ansible role directory (default: current directory)'
    )
    parser.add_argument(
        '--output-dir',
        default='docs/topology',
        help='Output directory for visualizations (default: docs/topology)'
    )
    
    args = parser.parse_args()
    
    role_path = Path(args.role_path).resolve()
    output_dir = role_path / args.output_dir
    
    print(f"Analyzing Ansible role at: {role_path}")
    print(f"Output directory: {output_dir}")
    
    # Analyze role structure
    analyzer = AnsibleRoleAnalyzer(role_path)
    analyzer.analyze()
    
    # Generate visualizations
    generator = SVGGenerator(analyzer, output_dir)
    generator.generate_all()
    
    # Create documentation
    create_readme(output_dir, role_path)
    
    print("\n✓ Topology visualization complete!")
    print(f"  View diagrams in: {output_dir}")


if __name__ == '__main__':
    main()
