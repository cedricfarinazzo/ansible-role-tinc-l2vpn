#!/usr/bin/env python3
"""
Documentation Drift Detector for Ansible Role

Detects inconsistencies between README.md documentation and defaults/main.yml
actual configuration values.
"""

import re
import yaml
from pathlib import Path
from typing import Dict, List, Tuple, Set


class DocDriftDetector:
    """Detects documentation drift between README and defaults."""
    
    def __init__(self, readme_path: str = "README.md", 
                 defaults_path: str = "defaults/main.yml"):
        self.readme_path = Path(readme_path)
        self.defaults_path = Path(defaults_path)
        self.readme_vars = {}
        self.defaults_vars = {}
        
    def parse_defaults(self) -> Dict[str, any]:
        """Parse defaults/main.yml to extract variable definitions."""
        with open(self.defaults_path, 'r') as f:
            data = yaml.safe_load(f)
        return data if data else {}
    
    def parse_readme_vars(self) -> Dict[str, str]:
        """Extract variable definitions from README.md."""
        with open(self.readme_path, 'r') as f:
            content = f.read()
        
        vars_dict = {}
        
        # Pattern to match YAML variable definitions in code blocks
        # Matches: variable_name: value  # comment
        pattern = r'^([a-z_][a-z0-9_]*)\s*:\s*([^\s#]+|"[^"]*"|\'[^\']*\')'
        
        for line in content.split('\n'):
            match = re.match(pattern, line.strip())
            if match:
                var_name = match.group(1)
                var_value = match.group(2).strip()
                
                # Clean up value - remove quotes if present
                if (var_value.startswith('"') and var_value.endswith('"')) or \
                   (var_value.startswith("'") and var_value.endswith("'")):
                    var_value = var_value[1:-1]
                
                vars_dict[var_name] = var_value
        
        return vars_dict
    
    def normalize_value(self, value) -> str:
        """Normalize values for comparison."""
        if value is None or value == "":
            return ""
        if isinstance(value, bool):
            return str(value).lower()
        if isinstance(value, (int, float)):
            return str(value)
        if isinstance(value, list):
            if len(value) == 0:
                return "[]"
            return str(value)
        return str(value)
    
    def compare_values(self, readme_val: str, default_val) -> bool:
        """Compare README and defaults values."""
        readme_normalized = self.normalize_value(readme_val)
        default_normalized = self.normalize_value(default_val)
        return readme_normalized == default_normalized
    
    def detect_drift(self) -> Tuple[List[Dict], List[str], List[str]]:
        """
        Detect documentation drift.
        
        Returns:
            Tuple of (mismatches, undocumented, non_existent)
        """
        self.readme_vars = self.parse_readme_vars()
        self.defaults_vars = self.parse_defaults()
        
        mismatches = []
        undocumented = []
        non_existent = []
        
        # Find mismatches and non-existent variables
        for var_name, readme_value in self.readme_vars.items():
            if var_name in self.defaults_vars:
                default_value = self.defaults_vars[var_name]
                if not self.compare_values(readme_value, default_value):
                    mismatches.append({
                        'variable': var_name,
                        'readme_value': readme_value,
                        'actual_value': self.normalize_value(default_value)
                    })
            else:
                non_existent.append(var_name)
        
        # Find undocumented variables
        for var_name in self.defaults_vars.keys():
            if var_name not in self.readme_vars:
                undocumented.append(var_name)
        
        return mismatches, undocumented, non_existent
    
    def generate_report(self) -> str:
        """Generate a markdown report of drift issues."""
        mismatches, undocumented, non_existent = self.detect_drift()
        
        report_lines = [
            "# Documentation Drift Report",
            "",
            f"Generated for ansible-role-tinc-l2vpn",
            "",
            "## Summary",
            "",
            f"- **Mismatched values**: {len(mismatches)}",
            f"- **Undocumented variables**: {len(undocumented)}",
            f"- **Non-existent documented variables**: {len(non_existent)}",
            "",
        ]
        
        if mismatches:
            report_lines.extend([
                "## ⚠️ Mismatched Values",
                "",
                "Variables where README documentation differs from actual defaults:",
                "",
                "| Variable | README Value | Actual Default |",
                "|----------|--------------|----------------|"
            ])
            for mismatch in mismatches:
                report_lines.append(
                    f"| `{mismatch['variable']}` | `{mismatch['readme_value']}` | "
                    f"`{mismatch['actual_value']}` |"
                )
            report_lines.append("")
        
        if undocumented:
            report_lines.extend([
                "## 📝 Undocumented Variables",
                "",
                "Variables defined in defaults/main.yml but not documented in README:",
                ""
            ])
            for var in sorted(undocumented):
                actual_value = self.normalize_value(self.defaults_vars[var])
                report_lines.append(f"- `{var}`: `{actual_value}`")
            report_lines.append("")
        
        if non_existent:
            report_lines.extend([
                "## ❌ Non-Existent Documented Variables",
                "",
                "Variables documented in README but not defined in defaults/main.yml:",
                ""
            ])
            for var in sorted(non_existent):
                readme_value = self.readme_vars[var]
                report_lines.append(f"- `{var}`: `{readme_value}` (documented)")
            report_lines.append("")
        
        if not mismatches and not undocumented and not non_existent:
            report_lines.extend([
                "## ✅ No Drift Detected",
                "",
                "All documentation is in sync with actual defaults!",
                ""
            ])
        
        return "\n".join(report_lines)


def main():
    """Main entry point."""
    detector = DocDriftDetector()
    report = detector.generate_report()
    
    # Write report to file
    report_path = Path("docs/drift-report.md")
    report_path.parent.mkdir(exist_ok=True)
    with open(report_path, 'w') as f:
        f.write(report)
    
    print(f"Documentation drift report generated: {report_path}")
    print()
    print(report)


if __name__ == "__main__":
    main()
