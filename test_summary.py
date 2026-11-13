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

    def test_length_retries_with_full_source_and_larger_budget(self):
        def response(reason, content):
            return types.SimpleNamespace(raise_for_status=lambda: None,
                json=lambda: {'done_reason': reason, 'message': {'content': content}})
        with patch.object(summary.requests, 'post', side_effect=[
                response('length', 'incomplet'), response('stop', 'Résumé complet')]) as post:
            self.assertEqual(summary.ask('SOURCE ENTIERE', 'résume'), 'Résumé complet')
            calls = post.call_args_list
            self.assertEqual([c.kwargs['json']['options']['num_predict'] for c in calls], [1800, 3000])
            for call in calls:
                self.assertIn('SOURCE ENTIERE', call.kwargs['json']['messages'][1]['content'])
                self.assertEqual(call.kwargs['json']['options']['num_ctx'], 8192)

    def test_all_truncated_attempts_are_bounded(self):
        response = types.SimpleNamespace(raise_for_status=lambda: None,
            json=lambda: {'done_reason': 'length', 'message': {'content': 'incomplet'}})
        with patch.object(summary.requests, 'post', return_value=response) as post:
            with self.assertRaises(RuntimeError):
                summary.ask('source', 'résume')
            self.assertEqual(post.call_count, 3)

    def test_http_failure_is_not_retried(self):
        response = types.SimpleNamespace(raise_for_status=lambda: (_ for _ in ()).throw(RuntimeError('HTTP')))
        with patch.object(summary.requests, 'post', return_value=response) as post:
            with self.assertRaisesRegex(RuntimeError, 'HTTP'):
                summary.ask('source', 'résume')
            self.assertEqual(post.call_count, 1)

if __name__ == '__main__':
    unittest.main()

