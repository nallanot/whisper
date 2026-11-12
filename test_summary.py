import sys
import types
import unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0, str(Path(__file__).parent / 'app'))
sys.modules.setdefault('requests', types.SimpleNamespace(post=None))
import summary

class SummaryTests(unittest.TestCase):
    def test_no_text_lost(self):
        source = 'Échéance : lundi.\n' * 2000
        parts = summary.chunks(source)
        self.assertEqual(''.join(parts), source)
        self.assertTrue(all(len(x) <= 6500 for x in parts))

    def test_all_parts_analyzed(self):
        with patch.object(summary, 'ask', return_value='Note conservée') as ask:
            summary.summarize('a' * 14000)
            self.assertEqual(ask.call_count, 4)
            self.assertEqual(''.join(call.args[0] for call in ask.call_args_list[:3]), 'a' * 14000)

    def test_hierarchical_reduction(self):
        def model(text, instruction):
            return 'n' * 4000 if instruction.startswith('Extrais') else 'synthèse'
        with patch.object(summary, 'ask', side_effect=model) as ask:
            summary.summarize('a' * 20000)
            self.assertEqual(ask.call_count, 7)

    def test_truncated_response_rejected(self):
        response = types.SimpleNamespace(raise_for_status=lambda: None,
            json=lambda: {'done_reason': 'length', 'message': {'content': 'incomplet'}})
        with patch.object(summary.requests, 'post', return_value=response):
            with self.assertRaises(RuntimeError):
                summary.ask('source', 'résume')

if __name__ == '__main__':
    unittest.main()
