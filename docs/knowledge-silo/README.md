Knowledge Silo Detector

Purpose
- Identify likely knowledge silos by analysing git commit history and repository metadata over a configurable time window (default: 12 months).

How it works (minimal)
- Aggregates commits per top-level directory and author
- Flags directories where a single author accounts for >= commit_share_threshold (default 50%) of commits and the directory has at least min_commits (default 10)

Running locally
- scripts/run_knowledge_silo_detector.sh
- Outputs: output/scripts/knowledge_silo_report.json and output/summary.txt

Configuration
- scripts/knowledge_silo_config.yml contains thresholds and time window

Assumptions & limitations
- Uses git history only for initial pass. PR/issue and CODEOWNERS analysis is optional and not included in first-pass to keep tooling lightweight.
- Time window defaults to last 12 months.
- Does not make personnel actions; results are signals for maintainers to investigate.

Privacy
- Avoid publishing raw personal contribution counts without consent. Use aggregated results and anonymise when necessary.
