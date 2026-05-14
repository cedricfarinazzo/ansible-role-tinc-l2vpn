#!/usr/bin/env python3
"""Knowledge Silo Detector

Writes JSON report to output/scripts/knowledge_silo_report.json and summary to output/summary.txt

Minimal, dependency-light script that analyses git commits in a configurable time window
and flags directories where a single author has a large share of commits.
"""

from __future__ import annotations
import argparse
import json
import os
import subprocess
import sys
from collections import defaultdict
from datetime import datetime, timedelta
import yaml
import logging

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

DEFAULT_CONFIG_PATH = os.path.join(os.path.dirname(__file__), "knowledge_silo_config.yml")


def load_config(path: str | None):
    path = path or DEFAULT_CONFIG_PATH
    if not os.path.exists(path):
        # defaults
        return {
            "commit_share_threshold": 0.5,
            "min_commits": 10,
            "time_window_months": 12,
        }
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def git_commits_since(since_date: datetime) -> list[dict]:
    # Use ASCII unit/record separators to parse
    fmt = "%H%x1F%an%x1F%ae%x1E"
    cmd = [
        "git",
        "log",
        f"--since={since_date.isoformat()}",
        f"--pretty=format:{fmt}",
        "--name-only",
    ]
    try:
        out = subprocess.check_output(cmd, text=True, stderr=subprocess.DEVNULL)
    except subprocess.CalledProcessError as e:
        logging.error("git command failed: %s", e)
        raise
    entries = out.split("\x1E")
    commits = []
    for ent in entries:
        ent = ent.strip()
        if not ent:
            continue
        parts = ent.split("\x1F")
        if len(parts) < 3:
            continue
        commit_hash, author_name, author_email = parts[:3]
        # remaining lines are filenames
        rest = ent.split("\n")[1:]
        files = [r.strip() for r in rest if r.strip()]
        commits.append({
            "hash": commit_hash,
            "author_name": author_name,
            "author_email": author_email,
            "files": files,
        })
    return commits


def top_level_dir(path: str) -> str:
    if not path or path.startswith("."):
        return "."
    parts = path.split("/")
    return parts[0] if parts else "."


def aggregate_commits(commits: list[dict]) -> dict:
    # counts[dir][author] = commits touching that dir (commit counted once per dir)
    counts = defaultdict(lambda: defaultdict(int))
    total_per_dir = defaultdict(int)
    for c in commits:
        author = f"{c['author_name']} <{c['author_email']}>"
        touched_dirs = set()
        for f in c.get("files", []):
            d = top_level_dir(f)
            touched_dirs.add(d)
        if not touched_dirs:
            touched_dirs.add(".")
        for d in touched_dirs:
            counts[d][author] += 1
            total_per_dir[d] += 1
    return {"counts": counts, "total": total_per_dir}


def detect_silos(agg: dict, config: dict) -> list[dict]:
    flags = []
    threshold = config.get("commit_share_threshold", 0.5)
    min_commits = config.get("min_commits", 10)
    counts = agg["counts"]
    total = agg["total"]
    for d, authors in counts.items():
        t = total.get(d, 0)
        if t < min_commits:
            continue
        # find top author
        top_author, top_count = max(authors.items(), key=lambda it: it[1])
        share = top_count / t if t else 0.0
        if share >= threshold:
            flags.append({
                "directory": d,
                "top_author": top_author,
                "top_count": top_count,
                "total_commits": t,
                "share": round(share, 3),
            })
    return flags


def write_report(output_dir: str, report: dict):
    os.makedirs(output_dir, exist_ok=True)
    json_path = os.path.join(output_dir, "scripts/knowledge_silo_report.json")
    summary_path = os.path.join(output_dir, "summary.txt")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    # human summary
    lines = []
    if report.get("flags"):
        lines.append("Potential knowledge silos detected:\n")
        for f in report["flags"]:
            lines.append(
                f"Directory: {f['directory']}\nTop author: {f['top_author']} ({f['top_count']}/{f['total_commits']} commits, share={f['share']})\n"
            )
    else:
        lines.append("No likely knowledge silos detected with current thresholds.\n")
    with open(summary_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    return json_path, summary_path


def main(argv=None):
    p = argparse.ArgumentParser(description="Knowledge Silo Detector")
    p.add_argument("--config", help="Path to YAML config")
    p.add_argument("--output", default="output", help="Output directory")
    p.add_argument("--now", help=argparse.SUPPRESS)
    args = p.parse_args(argv)
    try:
        cfg = load_config(args.config)
    except Exception as e:
        logging.error("Failed to load config: %s", e)
        return 2
    months = int(cfg.get("time_window_months", 12))
    if args.now:
        now = datetime.fromisoformat(args.now)
    else:
        now = datetime.now()
    since = now - timedelta(days=30 * months)
    try:
        commits = git_commits_since(since)
    except Exception:
        logging.exception("Failed to collect git commits")
        return 3
    agg = aggregate_commits(commits)
    flags = detect_silos(agg, cfg)
    report = {
        "generated_at": now.isoformat(),
        "config": cfg,
        "total_commits_analyzed": sum(agg["total"].values()),
        "flags": flags,
    }
    json_path, summary_path = write_report(args.output, report)
    logging.info("Report written: %s", json_path)
    logging.info("Summary written: %s", summary_path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
