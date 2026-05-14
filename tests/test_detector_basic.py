import unittest
from scripts import knowledge_silo_detector as ksd

class TestDetectorBasic(unittest.TestCase):
    def test_aggregate_and_detect(self):
        # synthetic commits touching two top-level dirs 'a' and 'b'
        commits = [
            {"hash":"1","author_name":"Alice","author_email":"a@example.com","files":["a/f1.py"]},
            {"hash":"2","author_name":"Alice","author_email":"a@example.com","files":["a/f2.py"]},
            {"hash":"3","author_name":"Bob","author_email":"b@example.com","files":["a/f3.py"]},
            {"hash":"4","author_name":"Alice","author_email":"a@example.com","files":["b/f4.py"]},
            {"hash":"5","author_name":"Alice","author_email":"a@example.com","files":["a/f5.py"]},
            {"hash":"6","author_name":"Alice","author_email":"a@example.com","files":["a/f6.py"]},
        ]
        agg = ksd.aggregate_commits(commits)
        # total commits touching 'a' should be 5 (Alice 4, Bob 1)
        self.assertEqual(agg['total'].get('a'), 5)
        cfg = {"commit_share_threshold": 0.6, "min_commits": 3}
        flags = ksd.detect_silos(agg, cfg)
        # Expect 'a' to be flagged since Alice did 4/5 = 0.8
        self.assertTrue(any(f['directory'] == 'a' for f in flags))

if __name__ == '__main__':
    unittest.main()
