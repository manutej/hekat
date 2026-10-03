"""Tests for the testing/monitoring layer: adversarial suite, OpenRouter runner, server.

No network: keys are dropped so agents mock and classification is local.
"""

import os
import unittest
from unittest import mock


def _no_keys():
    return mock.patch.dict(os.environ, {}, clear=False)


class TestAdversarialSuite(unittest.TestCase):
    def setUp(self):
        os.environ.pop("OPENROUTER_API_KEY", None)
        os.environ.pop("TYPESAFE_API_KEY", None)

    def test_gate_suite_all_pass(self):
        import hekat_eval as E
        results = E.run_gate_suite()
        self.assertEqual(len(results), len(E.GATE_CASES))
        for r in results:
            self.assertTrue(r.passed, f"{r.name}: expected {r.expected}, got {r.got}")

    def test_suite_includes_block_and_allow(self):
        import hekat_eval as E
        verdicts = {c.expected for c in E.GATE_CASES}
        self.assertIn("RED", verdicts)    # must-block cases
        self.assertIn("GREEN", verdicts)  # false-positive guards
        self.assertIn("AMBER", verdicts)

    def test_probes_skipped_without_key(self):
        import hekat_eval as E
        probes = E.run_agent_probes()
        self.assertTrue(all(p.got == "SKIPPED" for p in probes))
        self.assertTrue(all(p.passed for p in probes))  # skipped counts as non-failing

    def test_run_suite_summary(self):
        import hekat_eval as E
        res = E.run_suite()
        self.assertTrue(res["summary"]["all_passed"])
        self.assertEqual(res["summary"]["openrouter_live"], False)


class TestOpenRouter(unittest.TestCase):
    def setUp(self):
        os.environ.pop("OPENROUTER_API_KEY", None)

    def test_mock_when_no_key(self):
        import hekat_openrouter as O
        r = O.run_agent("deep-researcher", "find facts")
        self.assertFalse(r.live)
        self.assertIn("MOCK", r.output)

    def test_client_requires_key(self):
        import hekat_openrouter as O
        from hekat_jev_config import NotConfigured
        with self.assertRaises(NotConfigured):
            O.OpenRouterClient().chat([{"role": "user", "content": "hi"}])

    def test_live_path_with_mocked_client(self):
        import hekat_openrouter as O
        with mock.patch.dict(os.environ, {"OPENROUTER_API_KEY": "sk-x"}, clear=False):
            with mock.patch.object(O.OpenRouterClient, "chat", return_value="measured: 3 passing tests"):
                r = O.run_agent("test-engineer", "report results")
                self.assertTrue(r.live)
                self.assertIn("measured", r.output)


class TestServer(unittest.TestCase):
    def setUp(self):
        os.environ.pop("OPENROUTER_API_KEY", None)
        os.environ.pop("TYPESAFE_API_KEY", None)

    def test_classify_query_shape(self):
        import hekat_serve as S
        o = S.classify_query('deep-researcher -> api-architect -> practical-programmer : "x"')
        self.assertIn(o["verdict"], ("GREEN", "AMBER", "RED"))
        self.assertEqual(len(o["nodes"]), 3)
        self.assertTrue(o["phases"])
        self.assertIn("allowed_mass", o)

    def test_classify_forbid_action_fails_closed(self):
        import hekat_serve as S
        o = S.classify_query('deep-researcher -> deployment-orchestrator : "audit"', forbid=["action"])
        self.assertEqual(o["verdict"], "RED")

    def test_run_query_classifies_each_output(self):
        import hekat_serve as S
        before = len(S.RUNS)
        r = S.run_query('deep-researcher -> test-engineer : "verify"', "run tests")
        self.assertEqual(len(r["agents"]), 2)
        for a in r["agents"]:
            self.assertIn(a["output_verdict"], ("GREEN", "AMBER", "RED"))
            self.assertIn(a["output_color"], ["entity", "concept", "idea", "evidence", "action"])
            self.assertFalse(a["live"])  # mock
        self.assertEqual(len(S.RUNS), before + 1)

    def test_invalid_query_raises(self):
        import hekat_serve as S
        with self.assertRaises(ValueError):
            S.classify_query('not-a-real-agent -> another-fake : "x"')


if __name__ == "__main__":
    unittest.main(verbosity=2)
