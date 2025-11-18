"""HEKAT DSL Type Checker - Validates AST for semantic correctness."""

from typing import Dict, List, Set
from hekat_parser import (
    QueryNode, ExpressionNode, SimpleNode, SequentialNode, ParallelNode,
    FallbackNode, EnsembleNode, CommandedNode, SkilledNode
)


class TypeChecker:
    """Validates AST for semantic correctness."""

    def __init__(self):
        """Initialize with valid agents and skills from Claude Code."""
        # Valid agents from ~/.claude/agents/
        self.agents: Set[str] = {
            'api-architect', 'astro-data-manager', 'claude-plugin-marketplace-builder',
            'claude-sdk-expert', 'code-craftsman', 'code-trimmer',
            'context7-doc-reviewer', 'coverage-analyzer', 'debug-detective',
            'deep-researcher', 'deployment-orchestrator', 'devops-github-expert',
            'doc-rag-builder', 'docs-generator', 'flutter-app-builder',
            'frontend-architect', 'git-genius', 'github-workflow-expert',
            'hekat-agent', 'linear-mcp-orchestrator', 'mcp-integration-wizard',
            'mercurio-orchestrator', 'practical-programmer', 'project-orchestrator',
            'skill-builder', 'symbolic-visualizer', 'task-memory-manager',
            'tax-analyst', 'test-engineer', 'test-runner', 'unix-bash-expert',
            'unix-command-master', 'voice-mode-orchestrator',
            'wikijs-graphql-orchestrator', 'youtube-summarizer',
            'mars-agent', 'mercurio-agent'
        }

        # Valid skills from ~/.claude/skills/
        self.skills: Set[str] = {
            'alembic', 'angular-development', 'apache-airflow-orchestration',
            'apache-spark-data-processing', 'api-gateway-patterns',
            'asyncio-concurrency-patterns', 'aws-cloud-architecture',
            'aws-cloud-services', 'axum-web-framework', 'ci-cd-pipeline-patterns',
            'claude-agent-sdk-multiplatform', 'claude-sdk-integration-patterns',
            'database-management-patterns', 'dbt-data-transformation',
            'docker-compose-orchestration', 'dsl-orchestration',
            'enterprise-architecture-patterns', 'express-microservices-architecture',
            'expressjs-development', 'fastapi', 'fastapi-development',
            'fastapi-microservices-development', 'figma-design',
            'frontend-architecture', 'golang-backend-development',
            'graphql-api-development', 'grpc-microservices',
            'hasura-graphql-engine', 'hekat', 'javascript-fundamentals',
            'jest-react-testing', 'kafka-stream-processing',
            'kubernetes-orchestration', 'langchain-orchestration',
            'linear-dev-accelerator', 'luxor-projects-reference',
            'mcp-integration-expert', 'microservices-patterns',
            'mixture-of-experts-agentic-modeling', 'mlops-workflows',
            'mobile-design', 'n8n-master', 'n8n-mcp-orchestrator',
            'nextjs-development', 'nodejs-development', 'oauth2-authentication',
            'observability-monitoring', 'pandas', 'performance-benchmark-specialist',
            'playwright-visual-testing', 'postgresql',
            'postgresql-database-engineering', 'psycopg', 'pydantic', 'pytest',
            'pytest-patterns', 'react-development', 'react-patterns',
            'redis-state-management', 'responsive-design',
            'rest-api-design-patterns', 'rust-systems-programming',
            'shell-testing-framework', 'spring-boot-development', 'sqlalchemy',
            'supabase-mcp-integration', 'svelte-development',
            'symbolic-architecture-visualization', 'tailwind-css',
            'terraform-infrastructure', 'terraform-infrastructure-as-code',
            'ui-design-patterns', 'unix-goto-development', 'ux-principles',
            'vector-database-management', 'vuejs-development', 'wireframing'
        }

        # Valid commands (from slash commands)
        self.commands: Set[str] = {
            'ctx7', 'workflows', 'crew', 'aprof', 'wflw', 'actualize',
            'meta-skill-builder', 'cheatsheet', 'sequential-thinking',
            'task-relay', 'mercurio', 'mars', 'hekat', 'coord'
        }

    def validate(self, query_node: QueryNode) -> Dict:
        """Validate entire query tree.

        Returns: {"valid": bool, "errors": list, "warnings": list}
        """
        errors: List[str] = []
        warnings: List[str] = []

        # Validate expression tree
        self._validate_expression(query_node.expression, errors, warnings)

        # Validate prompt is not empty
        if not query_node.prompt or not query_node.prompt.strip():
            errors.append("Query prompt cannot be empty")

        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        }

    def _validate_expression(
        self,
        expr: ExpressionNode,
        errors: List[str],
        warnings: List[str]
    ) -> None:
        """Recursively validate expression nodes."""
        if isinstance(expr, SimpleNode):
            self._validate_simple(expr, errors, warnings)

        elif isinstance(expr, SkilledNode):
            self._validate_skilled(expr, errors, warnings)

        elif isinstance(expr, CommandedNode):
            self._validate_commanded(expr, errors, warnings)

        elif isinstance(expr, EnsembleNode):
            self._validate_ensemble(expr, errors, warnings)

        elif isinstance(expr, SequentialNode):
            for step in expr.steps:
                self._validate_expression(step, errors, warnings)

        elif isinstance(expr, ParallelNode):
            if len(expr.branches) < 2:
                errors.append("Parallel expression must have at least 2 branches")
            for branch in expr.branches:
                self._validate_expression(branch, errors, warnings)

        elif isinstance(expr, FallbackNode):
            if len(expr.alternatives) < 2:
                errors.append("Fallback expression must have at least 2 alternatives")
            for alternative in expr.alternatives:
                self._validate_expression(alternative, errors, warnings)

    def _validate_simple(
        self,
        node: SimpleNode,
        errors: List[str],
        warnings: List[str]
    ) -> None:
        """Validate SimpleNode - agent name must exist."""
        if node.name not in self.agents:
            errors.append(f"Agent '{node.name}' not found")

    def _validate_skilled(
        self,
        node: SkilledNode,
        errors: List[str],
        warnings: List[str]
    ) -> None:
        """Validate SkilledNode - agent and skills must exist."""
        if node.agent not in self.agents:
            errors.append(f"Agent '{node.agent}' not found")

        for skill in node.skills:
            if skill not in self.skills:
                errors.append(f"Skill '{skill}' not found")

        if len(node.skills) == 0:
            errors.append("SkilledNode must have at least one skill")

    def _validate_commanded(
        self,
        node: CommandedNode,
        errors: List[str],
        warnings: List[str]
    ) -> None:
        """Validate CommandedNode - command and agents must exist."""
        if node.command not in self.commands:
            warnings.append(
                f"Command '{node.command}' not recognized (may be external)"
            )

        for agent in node.agents:
            if agent not in self.agents:
                errors.append(f"Agent '{agent}' not found in commanded pattern")

        if len(node.agents) == 0:
            errors.append("CommandedNode must have at least one agent")

    def _validate_ensemble(
        self,
        node: EnsembleNode,
        errors: List[str],
        warnings: List[str]
    ) -> None:
        """Validate EnsembleNode - base agent and steps must be valid."""
        if node.base not in self.agents:
            errors.append(f"Ensemble base agent '{node.base}' not found")

        if node.count < 1 or node.count > 10:
            errors.append(
                f"Ensemble count must be between 1 and 10 (got {node.count})"
            )

        # merge and synth steps are typically operations, not agents
        # We'll just check they're not empty
        if not node.merge_step:
            errors.append("Ensemble merge_step cannot be empty")
        if not node.synth_step:
            errors.append("Ensemble synth_step cannot be empty")
