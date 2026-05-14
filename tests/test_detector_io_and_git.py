import sys, os
# Ensure repo root is on sys.path so 'scripts' package can be imported when running this file directly
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from scripts import knowledge_silo_detector as ksd


def run_tests():
    # Build synthetic commits: 3 commits touching module
    commits = [
        {"hash": "abc123", "author_name": "Alice", "author_email": "alice@example.com", "files": ["module/a.py"]},
        {"hash": "def456", "author_name": "Bob", "author_email": "bob@example.com", "files": ["module/b.py", "module/c.py"]},
        {"hash": "abc124", "author_name": "Alice", "author_email": "alice@example.com", "files": ["module/a.py"]},
    ]
    agg = ksd.aggregate_commits(commits)
    assert 'module' in agg['total']
    assert agg['total']['module'] == 3
    flags = ksd.detect_silos(agg, {"commit_share_threshold": 0.5, "min_commits": 1})
    # Alice has 2/3 commits -> share ~0.66, should be flagged
    assert len(flags) == 1
    f = flags[0]
    assert f['directory'] == 'module'
    assert 'Alice' in f['top_author']
    print('All tests passed')


if __name__ == '__main__':
    try:
        run_tests()
    except AssertionError as e:
        print('Tests failed:', e)
        sys.exit(1)
    sys.exit(0)
