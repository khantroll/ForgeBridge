import os
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from windows_replace_probe import probe


@unittest.skipUnless(os.name == 'nt', 'Windows native file-API control')
class WindowsReplaceProbeTests(unittest.TestCase):
    def test_unheld_replacement_and_deliberately_blocked_target_are_distinct(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            free=root/'free'; free.mkdir()
            held=root/'held'; held.mkdir()
            result=probe(free)
            self.assertTrue(result['move_ok'] or result['replace_ok'])
            blocked=probe(held,hold_target=True)
            self.assertTrue(blocked['expected_block_observed'])
            self.assertNotEqual(blocked['replace_error'],0)
            # The diagnostic never overwrites existing inputs, even its own.
            before=(held/'CURRENT').read_bytes()
            with self.assertRaises(FileExistsError): probe(held)
            self.assertEqual((held/'CURRENT').read_bytes(),before)


if __name__ == '__main__':
    unittest.main()
