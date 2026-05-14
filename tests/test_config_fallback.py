import sys, os
# Ensure repo root is on sys.path when running directly
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import tempfile
from scripts import knowledge_silo_detector as ksd


def test_load_config_fallback_casting():
    # Force fallback parser behavior
    ksd.yaml = None
    content = """
commit_share_threshold: 0.75
min_commits: 5
time_window_months: 6
"""
    with tempfile.NamedTemporaryFile("w", delete=False) as tf:
        tf.write(content)
        tf_path = tf.name
    try:
        cfg = ksd.load_config(tf_path)
        assert isinstance(cfg["commit_share_threshold"], float)
        assert cfg["commit_share_threshold"] == 0.75
        assert isinstance(cfg["min_commits"], int)
        assert cfg["min_commits"] == 5
        assert isinstance(cfg["time_window_months"], int)
        assert cfg["time_window_months"] == 6
    finally:
        os.unlink(tf_path)
