"""
DSL Parser for keyboard-friendly comonadic syntax.

Syntax:
  operation[args]:mode | next_op | final^extract

Symbols:
  * = infinite loop
  >> = feedback/iterate
  ^ = extract
  | = pipe to next
  [] = multi-agent/args
  <> = window/focus
  & = consensus/and
  : = mode specifier
"""

import re
from dataclasses import dataclass
from typing import List, Optional, Callable, Any
from enum import Enum


class OperationType(Enum):
    """Types of comonadic operations."""
    COLLECT = "collect"
    VALIDATE = "validate"
    CRITIQUE = "critique"
    COPY = "copy"
    CONSENSUS = "consensus"
    SCORE = "score"
    VERIFY = "verify"
    EXTRACT = "extract"
    ITERATE = "iterate"
    CUSTOM = "custom"


@dataclass
class DSLArgument:
    """Represents arguments in DSL syntax."""
    name: str
    mode: str = ""  # e.g., "converge", "lazy", "weighted"
    threshold: Optional[float] = None
    agents: List[str] = None

    def __post_init__(self):
        if self.agents is None:
            self.agents = []


@dataclass
class DSLOperation:
    """Single operation in DSL."""
    op_type: OperationType
    name: str
    args: DSLArgument
    next_op: Optional['DSLOperation'] = None

    def __repr__(self) -> str:
        return f"{self.name}[{self.args.agents}]:{self.args.mode}"


class DSLParser:
    """Parse keyboard-friendly DSL syntax."""

    def __init__(self):
        self.patterns = {
            # collect[*]:converge
            'collect': r'collect\[\*\]:(\w+)',
            # validate[fact,bias]:filter
            'validate': r'validate\[([^\]]+)\]:(\w+)',
            # critique>>improve^0.9
            'critique': r'critique>>(\w+)\^([\d.]+)',
            # copy[]agent1,agent2,agent3
            'copy': r'copy\[\]([^\]]+)',
            # consensus<>weighted
            'consensus': r'consensus<>(\w+)',
            # score and verify
            'score': r'score>>(\w+)\^([\d.]+)',
            # extract with ^
            'extract': r'\^ ?(\w+)?',
            # pipe
            'pipe': r'\|',
        }

    def parse(self, dsl_string: str) -> DSLOperation:
        """Parse DSL string into operation tree."""
        # Remove whitespace, keep pipes as separators
        dsl_string = dsl_string.strip()

        # Split by pipes to get operations
        parts = [p.strip() for p in dsl_string.split('|')]

        # Parse first operation
        first_op = self._parse_single_operation(parts[0])

        # Chain remaining operations
        current = first_op
        for part in parts[1:]:
            next_op = self._parse_single_operation(part)
            current.next_op = next_op
            current = next_op

        return first_op

    def _parse_single_operation(self, op_str: str) -> DSLOperation:
        """Parse single operation from string."""
        op_str = op_str.strip()

        # Try each pattern
        if 'collect[*]' in op_str:
            match = re.search(self.patterns['collect'], op_str)
            if match:
                mode = match.group(1)
                return DSLOperation(
                    op_type=OperationType.COLLECT,
                    name="collect",
                    args=DSLArgument(name="collect", mode=mode)
                )

        elif 'validate[' in op_str:
            match = re.search(self.patterns['validate'], op_str)
            if match:
                agents_str = match.group(1)
                mode = match.group(2)
                agents = [a.strip() for a in agents_str.split(',')]
                return DSLOperation(
                    op_type=OperationType.VALIDATE,
                    name="validate",
                    args=DSLArgument(name="validate", mode=mode, agents=agents)
                )

        elif 'critique>>' in op_str:
            match = re.search(self.patterns['critique'], op_str)
            if match:
                improve_mode = match.group(1)
                threshold = float(match.group(2))
                return DSLOperation(
                    op_type=OperationType.CRITIQUE,
                    name="critique",
                    args=DSLArgument(
                        name="critique",
                        mode=improve_mode,
                        threshold=threshold
                    )
                )

        elif 'copy[]' in op_str:
            match = re.search(self.patterns['copy'], op_str)
            if match:
                agents_str = match.group(1)
                agents = [a.strip() for a in agents_str.split(',')]
                return DSLOperation(
                    op_type=OperationType.COPY,
                    name="copy",
                    args=DSLArgument(name="copy", agents=agents)
                )

        elif 'consensus<>' in op_str:
            match = re.search(self.patterns['consensus'], op_str)
            if match:
                mode = match.group(1)
                return DSLOperation(
                    op_type=OperationType.CONSENSUS,
                    name="consensus",
                    args=DSLArgument(name="consensus", mode=mode)
                )

        elif 'score>>' in op_str:
            match = re.search(self.patterns['score'], op_str)
            if match:
                mode = match.group(1)
                threshold = float(match.group(2))
                return DSLOperation(
                    op_type=OperationType.SCORE,
                    name="score",
                    args=DSLArgument(
                        name="score",
                        mode=mode,
                        threshold=threshold
                    )
                )

        elif op_str.startswith('^'):
            match = re.search(self.patterns['extract'], op_str)
            if match:
                name = match.group(1) or "result"
                return DSLOperation(
                    op_type=OperationType.EXTRACT,
                    name="extract",
                    args=DSLArgument(name=name)
                )

        elif 'verify' in op_str:
            return DSLOperation(
                op_type=OperationType.VERIFY,
                name="verify",
                args=DSLArgument(name="verify")
            )

        else:
            # Custom operation
            return DSLOperation(
                op_type=OperationType.CUSTOM,
                name=op_str,
                args=DSLArgument(name=op_str)
            )

    def validate(self, operation: DSLOperation) -> List[str]:
        """Validate operation chain. Returns list of errors."""
        errors = []
        current = operation

        while current:
            # Check operation validity
            if current.op_type == OperationType.EXTRACT and current.next_op:
                errors.append("Extract (^) must be final operation")

            # Check threshold validity
            if current.args.threshold is not None:
                if not (0 <= current.args.threshold <= 1.0):
                    errors.append(
                        f"Threshold {current.args.threshold} must be between 0 and 1"
                    )

            current = current.next_op

        return errors

    def to_readable_form(self, operation: DSLOperation) -> str:
        """Convert operation tree back to readable DSL."""
        parts = []
        current = operation

        while current:
            if current.op_type == OperationType.COLLECT:
                parts.append(f"collect[*]:{current.args.mode}")
            elif current.op_type == OperationType.VALIDATE:
                agents = ",".join(current.args.agents)
                parts.append(f"validate[{agents}]:{current.args.mode}")
            elif current.op_type == OperationType.CRITIQUE:
                parts.append(f"critique>>{current.args.mode}^{current.args.threshold}")
            elif current.op_type == OperationType.COPY:
                agents = ",".join(current.args.agents)
                parts.append(f"copy[]{agents}")
            elif current.op_type == OperationType.CONSENSUS:
                parts.append(f"consensus<>{current.args.mode}")
            elif current.op_type == OperationType.EXTRACT:
                parts.append(f"^ {current.args.name}")
            else:
                parts.append(current.name)

            current = current.next_op

        return " | ".join(parts)


# Test the parser
if __name__ == "__main__":
    parser = DSLParser()

    # Test case 1: Research synthesis
    dsl1 = "collect[*]:converge | validate[fact,bias]:filter | critique>>improve^0.9 | ^ final"
    op1 = parser.parse(dsl1)
    print("DSL 1 (Research):")
    print(f"  Input: {dsl1}")
    print(f"  Parsed: {parser.to_readable_form(op1)}")
    print(f"  Errors: {parser.validate(op1)}")
    print()

    # Test case 2: Code review
    dsl2 = "copy[]security,performance,readability | consensus<>weighted | ^ review"
    op2 = parser.parse(dsl2)
    print("DSL 2 (Code Review):")
    print(f"  Input: {dsl2}")
    print(f"  Parsed: {parser.to_readable_form(op2)}")
    print(f"  Errors: {parser.validate(op2)}")
