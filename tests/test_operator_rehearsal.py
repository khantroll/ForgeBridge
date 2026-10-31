"""Public CLI relocation and non-success checks across synthetic scene profiles."""
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from rehearse_scene_import import rehearse


class OperatorRehearsalTests(unittest.TestCase):
    def test_relocated_profiles_build_without_original_paths_and_refuse_unsafe_updates(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / 'operator rehearsal'
            result = rehearse(root)
            self.assertEqual(result['status'], 'PASS')
            self.assertTrue(result['source_unchanged'])
            self.assertTrue(result['original_paths_unavailable_during_build'])
            self.assertEqual([s['native_tokens'] for s in result['scenes']], [1, 1, 0])
            self.assertEqual([s['rejected_tokens'] for s in result['scenes']], [2, 2, 0])
            self.assertGreater(result['combined_closed_references'], 0)
            self.assertEqual(result['commands'], 18)
            before = (root/'results.json').read_bytes()
            with self.assertRaisesRegex(ValueError, 'nothing is overwritten'):
                rehearse(root)
            self.assertEqual((root/'results.json').read_bytes(), before)


if __name__ == '__main__':
    unittest.main()
