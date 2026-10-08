"""Tests for the HEKAT ⇄ JEV bridge and the ~color classification modifier."""

import unittest

from hekat_lexer import Lexer, TokenType
from hekat_parser import Parser, parse, SimpleNode, SkilledNode, SequentialNode
from hekat_type_checker import TypeChecker
from hekat_dag_builder import DAGBuilder
import hekat_jev as J


class TestColorModifier(unittest.TestCase):
    def test_lexer_emits_tilde(self):
        types = [t.type for t in Lexer("a~concept").tokenize()]
        self.assertIn(TokenType.TILDE, types)

    def test_simple_port_parsed(self):
        node = parse('deep-researcher~evidence : "x"').expression
        self.assertIsInstance(node, SimpleNode)
        self.assertEqual(node.port, "evidence")

    def test_simple_without_port_is_none(self):
        node = parse('deep-researcher : "x"').expression
        self.assertIsNone(node.port)

    def test_skilled_port_parsed(self):
        node = parse('api-architect + fastapi ~ concept : "x"').expression
        self.assertIsInstance(node, SkilledNode)
        self.assertEqual(node.port, "concept")

    def test_port_in_sequence(self):
        seq = parse('deep-researcher~evidence -> api-architect~concept : "x"').expression
        self.assertIsInstance(seq, SequentialNode)
        self.assertEqual(seq.steps[0].port, "evidence")
        self.assertEqual(seq.steps[1].port, "concept")

    def test_backward_compatible_existing_queries(self):
        # queries without ~ still parse to the same shapes
        for q in ['api-architect : "d"',
                  'a -> b : "d"'.replace("a", "deep-researcher").replace("b", "api-architect"),
                  'api-architect + fastapi : "d"']:
            self.assertIsNotNone(parse(q))


class TestTypeChecker(unittest.TestCase):
    def test_valid_color_accepted(self):
        v = TypeChecker().validate(parse('deep-researcher~evidence : "x"'))
        self.assertTrue(v["valid"], v["errors"])

    def test_invalid_color_rejected(self):
        v = TypeChecker().validate(parse('deep-researcher~purple : "x"'))
        self.assertFalse(v["valid"])
        self.assertTrue(any("Invalid JEV color" in e for e in v["errors"]))


class TestScoreFill(unittest.TestCase):
    def test_green(self):
        d = {"entity": 0, "concept": 0, "idea": 0, "evidence": 8, "action": 2}
        s = J.score_fill(d, {"evidence", "action"}, set())
        self.assertEqual(s.verdict, "GREEN")

    def test_red_low_allowed(self):
        d = {"entity": 0, "concept": 0, "idea": 10, "evidence": 0, "action": 0}
        s = J.score_fill(d, {"evidence", "action"}, set())
        self.assertEqual(s.verdict, "RED")

    def test_red_toxin_fail_closed(self):
        d = {"entity": 0, "concept": 0, "idea": 0, "evidence": 7, "action": 3}
        s = J.score_fill(d, {"evidence"}, {"action"})  # action forbidden
        self.assertEqual(s.verdict, "RED")
        self.assertTrue(any("Toxin" in r for r in s.reasons))

    def test_amber_midband(self):
        d = {"entity": 0, "concept": 5, "idea": 5, "evidence": 0, "action": 0}
        s = J.score_fill(d, {"concept"}, set())  # allowed=0.5 in (0.4,0.72)
        self.assertEqual(s.verdict, "AMBER")

    def test_normalize_sums_to_one(self):
        p = J.normalize({"entity": 1, "concept": 1, "idea": 0, "evidence": 0, "action": 0})
        self.assertAlmostEqual(sum(p.values()), 1.0)


class TestTriage(unittest.TestCase):
    def test_mapping(self):
        self.assertEqual(J.TRIAGE["GREEN"], "compose")
        self.assertEqual(J.TRIAGE["AMBER"], "escalate")
        self.assertEqual(J.TRIAGE["RED"], "refuse")


class TestClassify(unittest.TestCase):
    def test_modifier_overrides_lexicon(self):
        node = parse('deep-researcher~action : "x"').expression
        self.assertEqual(J.classify_expr_color(node), "action")  # ~ wins over evidence lexicon

    def test_lexicon_default(self):
        node = parse('deep-researcher : "x"').expression
        self.assertEqual(J.classify_expr_color(node), "evidence")

    def test_edge_gate_match_and_mismatch(self):
        self.assertTrue(J.gate_edge("concept", "action", "a", "b").ok)
        self.assertFalse(J.gate_edge("evidence", "concept", "a", "b").ok)


class TestOrchestration(unittest.TestCase):
    def _classify(self, dsl, **kw):
        ast = parse(dsl)
        dag = DAGBuilder().build(ast.expression)
        return J.classify_orchestration(ast, dag, **kw)

    def test_pure_idea_refused(self):
        res = self._classify('mercurio-orchestrator -> project-orchestrator : "brainstorm"')
        self.assertEqual(res.score.verdict, "RED")
        self.assertEqual(res.triage, "refuse")

    def test_forbid_action_fails_closed(self):
        res = self._classify(
            'deep-researcher -> deployment-orchestrator : "audit"',
            allowed={"evidence", "concept"}, forbidden={"action"})
        self.assertEqual(res.score.verdict, "RED")

    def test_tape_records_verdict(self):
        res = self._classify('deep-researcher -> test-engineer : "verify"')
        r = J.replay(res.tape)
        self.assertEqual(r["verdict"], res.score.verdict)
        self.assertGreater(r["events"], 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
