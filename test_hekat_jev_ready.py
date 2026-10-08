"""Tests for the 'ready to go live' layer: config, TypeSafe codec/client, runner.

No network: the live path is exercised with a mocked client so the switch is
verified without a real key.
"""

import json
import os
import unittest
from unittest import mock

import hekat_jev_config as cfgmod
import hekat_jev_typesafe as ts
from hekat_jev_tape import InProcessRunner, TemporalRunner, get_runner, GATE_WORD
from hekat_jev_config import JevConfig, NotConfigured
from hekat_parser import parse
from hekat_dag_builder import DAGBuilder


def _cfg(**over):
    base = dict(typesafe_api_key=None, typesafe_endpoint=ts.load_config().typesafe_endpoint,
                typesafe_model="jev-1.13.0", temporal_address=None,
                temporal_namespace="default", temporal_task_queue="hekat-jev",
                jev_tape_path=None)
    base.update(over)
    return JevConfig(**base)


class TestConfig(unittest.TestCase):
    def test_offline_by_default(self):
        c = _cfg()
        self.assertFalse(c.typesafe_live)
        self.assertFalse(c.temporal_live)
        self.assertIn("local classifier", c.banner())

    def test_live_when_keyed(self):
        c = _cfg(typesafe_api_key="sk-test", temporal_address="localhost:7233")
        self.assertTrue(c.typesafe_live)
        self.assertTrue(c.temporal_live)
        self.assertIn("LIVE", c.banner())

    def test_load_config_reads_env(self):
        with mock.patch.dict(os.environ, {"TYPESAFE_API_KEY": "sk-x"}, clear=False):
            self.assertTrue(cfgmod.load_config().typesafe_live)


class TestDotenv(unittest.TestCase):
    def test_parse_dotenv(self):
        import tempfile, os as _os
        fd, path = tempfile.mkstemp(suffix=".env")
        with _os.fdopen(fd, "w") as f:
            f.write('# comment\nexport TYPESAFE_API_KEY="sk-abc"\nTYPESAFE_MODEL=jev-1.13.0\n\nBAD LINE\n')
        try:
            d = cfgmod._parse_dotenv(path)
        finally:
            _os.remove(path)
        self.assertEqual(d["TYPESAFE_API_KEY"], "sk-abc")
        self.assertEqual(d["TYPESAFE_MODEL"], "jev-1.13.0")
        self.assertNotIn("BAD LINE", d)

    def test_real_env_wins_over_dotenv(self):
        with mock.patch.dict(os.environ, {"TYPESAFE_API_KEY": "from-env"}, clear=False):
            self.assertEqual(cfgmod._env({"TYPESAFE_API_KEY": "from-dotenv"}, "TYPESAFE_API_KEY"), "from-env")

    def test_dotenv_fills_gap(self):
        with mock.patch.dict(os.environ, {}, clear=False):
            os.environ.pop("TEMPORAL_ADDRESS", None)
            self.assertEqual(cfgmod._env({"TEMPORAL_ADDRESS": "host:7233"}, "TEMPORAL_ADDRESS"), "host:7233")


class TestTypeSafeCodec(unittest.TestCase):
    def test_build_request_is_valid(self):
        req = ts.build_request({"agent": "deep-researcher"}, "jev-1.13.0")
        self.assertIsNone(ts.validate_request(req))
        self.assertIn("gold_color", req["questions"])

    def test_validate_rejects_wrong_model(self):
        req = ts.build_request({"a": 1}, "jev-1.13.0")
        req["model"] = "jev-latest"
        self.assertIsNotNone(ts.validate_request(req))

    def test_answers_to_dist_from_probabilities(self):
        answers = {"gold_color": {"type": "choice", "choice": "evidence",
                                  "probabilities": {"evidence": 0.8, "concept": 0.2},
                                  "confidence": 0.9}}
        d = ts.answers_to_dist(answers)
        self.assertAlmostEqual(sum(d.values()), 1.0)
        self.assertGreater(d["evidence"], d["concept"])

    def test_answers_to_toxin(self):
        self.assertEqual(ts.answers_to_toxin({"toxin_color": {"choice": "action"}}), "action")
        self.assertIsNone(ts.answers_to_toxin({"toxin_color": {"choice": "none"}}))

    def test_make_color_fn_none_when_offline(self):
        self.assertIsNone(ts.make_color_fn(_cfg()))

    def test_make_color_fn_uses_client_when_keyed(self):
        c = _cfg(typesafe_api_key="sk-test")
        fake_answers = {"gold_color": {"choice": "idea",
                                       "probabilities": {"idea": 1.0}, "confidence": 1.0}}
        with mock.patch.object(ts.TypeSafeClient, "fill", return_value=fake_answers):
            fn = ts.make_color_fn(c)
            self.assertIsNotNone(fn)
            d = fn({"agent": "deep-researcher", "prompt": "x"})
            self.assertEqual(max(d, key=d.get), "idea")

    def test_color_fn_degrades_on_error(self):
        c = _cfg(typesafe_api_key="sk-test")
        with mock.patch.object(ts.TypeSafeClient, "fill", side_effect=ValueError("boom")):
            fn = ts.make_color_fn(c)
            d = fn({"agent": "x", "prompt": "run tests and measure coverage"})
            self.assertAlmostEqual(sum(d.values()), 1.0)  # fell back to local, still valid

    def test_client_fill_requires_key(self):
        with self.assertRaises(NotConfigured):
            ts.TypeSafeClient(_cfg()).fill({"a": 1})


class TestRunner(unittest.TestCase):
    def _dag(self, dsl):
        ast = parse(dsl)
        return ast, DAGBuilder().build(ast.expression)

    def test_in_process_start_query_signal(self):
        ast, dag = self._dag('deep-researcher -> test-engineer : "verify"')
        r = InProcessRunner(_cfg())
        rec = r.start(ast, dag, run_id="r1")
        self.assertEqual(rec.gate, GATE_WORD[rec.classification.score.verdict])
        self.assertEqual(r.query("r1")["run_id"], "r1")
        sig = r.signal("r1", "approve")
        self.assertEqual(sig["decision"], "approve")

    def test_cohorts_reflect_phases(self):
        ast, dag = self._dag('deep-researcher -> (api-architect || test-engineer) : "x"')
        rec = InProcessRunner(_cfg()).start(ast, dag)
        # phase 1 should have two parallel workers
        multi = [c for c in rec.cohorts if len(c.workers) > 1]
        self.assertTrue(multi)

    def test_get_runner_falls_back_to_in_process(self):
        self.assertIsInstance(get_runner(_cfg()), InProcessRunner)

    def test_temporal_preflight_reports_missing(self):
        tr = TemporalRunner(_cfg(temporal_address="localhost:7233"))
        self.assertIsNotNone(tr.preflight())  # SDK / jev-tape not present here

    def test_temporal_start_raises_when_unconfigured(self):
        ast, dag = self._dag('deep-researcher : "x"')
        with self.assertRaises(NotConfigured):
            TemporalRunner(_cfg(temporal_address="localhost:7233")).start(ast, dag)


class TestSchema(unittest.TestCase):
    def test_schema_parses_and_pins_model(self):
        with open("schema/hekat-orchestration.json") as f:
            s = json.load(f)
        self.assertEqual(s["pin"], "jev-1.13.0")
        self.assertEqual(s["thresholds"]["green"], 0.72)


if __name__ == "__main__":
    unittest.main(verbosity=2)
