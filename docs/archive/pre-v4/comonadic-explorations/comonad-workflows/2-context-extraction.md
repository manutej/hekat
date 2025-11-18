# Pattern 2: Context Extraction & Compression

**Comonadic Form**: `↓ → compress:cache → stream^lazy`

**Mathematical Definition**:
```
extract :: Comonad w => w a → a
extract_compressed :: Comonad w => w a → (summary, metadata)
```

**Purpose**: Compress context while preserving essential information, enabling efficient distribution to downstream agents.

---

## Abstract Definition

### Comonadic Operations

| Operation | Role | Description |
|-----------|------|---|
| `↓` (Extract) | Downward compression | Summarize full context to essentials |
| `→` (Direct) | Selective routing | Send compressed to specific downstream |
| `:cache` | Memoization | Remember what was compressed (for recovery) |
| `^lazy` | Lazy evaluation | Only decompress what's actually needed |

### Key Properties

- **Smart compression**: Remove noise while preserving signal
- **Selective retention**: Keep breakthrough insights, drop logs
- **Metadata tracking**: Record what was compressed (for context)
- **Recovery capability**: Decompress if needed downstream

### Compression Strategies

1. **Summari zation**: Narrative compression of long texts
2. **Extraction**: Pull out key facts/code snippets
3. **Lossy filtering**: Remove items below importance threshold
4. **Structural collapse**: Merge related items into categories

---

## Agents Used

### Primary Agents
- **deep-researcher**: Identify what's important to preserve
- **code-trimmer**: Extract essential code patterns
- **practical-programmer**: Decide what to keep

### Supporting Agents
- **docs-generator**: Write concise summaries
- **context7-doc-reviewer**: Analyze what matters in documentation
- **debug-detective**: Extract root causes from logs

### Workflows Used
- **research-to-documentation**: Extract knowledge → synthesize
- **code-refactoring-pipeline**: Trim non-essential code

---

## Example 1: Conversation History Compression

**Scenario**: Compress long conversation history before sending to analysis agent

**Comonadic Form**: `history → extract:summary → cache:[key_exchanges] → compress^1K`

**Implementation**:

```python
from dataclasses import dataclass
from typing import Optional

@dataclass
class ConversationContext:
    """Context with full conversation history"""
    messages: list[dict]  # Full message history
    summary_cache: Optional[str] = None
    compression_ratio: float = 0.0

    def extract(self, target_tokens: int = 1000) -> str:
        """
        Extract compressed conversation summary

        Compression strategy:
        1. Identify topic shifts (major transitions)
        2. Keep first/last exchange per topic
        3. Preserve any explicit summaries
        4. Compress using abstractive summarization
        """
        if self.summary_cache:
            return self.summary_cache

        # Group by topic
        topics = self._identify_topics()
        key_messages = self._extract_key_messages(topics)

        # Generate summary
        summary = deep_researcher_agent(
            messages=key_messages,
            style="concise",
            target_length=target_tokens
        )

        self.summary_cache = summary
        self.compression_ratio = len(str(self.messages)) / len(summary)

        return summary

    def _identify_topics(self) -> dict:
        """Identify topic shifts in conversation"""
        # Simplified: segment by long pauses or explicit topic changes
        topics = {"general": []}
        for i, msg in enumerate(self.messages):
            if msg.get("type") == "topic_change":
                current_topic = msg.get("topic", f"topic_{len(topics)}")
                topics[current_topic] = []
            else:
                topics.get("general", []).append(i)
        return topics

    def _extract_key_messages(self, topics: dict) -> list:
        """Extract key exchange from each topic"""
        key = []
        for topic, indices in topics.items():
            if indices:
                # First message of topic
                key.append(self.messages[indices[0]])
                # Last message of topic
                if len(indices) > 2:
                    key.append(self.messages[indices[-1]])
        return key

    def duplicate(self) -> 'ConversationContext':
        """Prepare for downstream use"""
        return ConversationContext(
            messages=self.messages,
            summary_cache=self.summary_cache,
            compression_ratio=self.compression_ratio
        )

# Usage
def compress_before_analysis(full_context: ConversationContext) -> str:
    """Extract and cache summary before sending to downstream agent"""
    compressed = full_context.extract(target_tokens=1000)

    print(f"Original: {len(str(full_context.messages))} chars")
    print(f"Compressed: {len(compressed)} chars")
    print(f"Ratio: {full_context.compression_ratio:.1f}:1")

    return compressed
```

**Comonadic Perspective**:
- `↓`: Extract pulls essential information from full context
- `:cache`: Summary is cached for recovery if needed
- `^lazy`: Full history not decompressed unless explicitly requested
- Result: Downstream agent works with 1K summary, not 50K full history

**Token Cost**:
- Analysis: ~200 tokens (compression decision)
- Summarization: ~500 tokens (generate summary)
- Total: ~700 tokens (vs 5K+ if sending full history)

---

## Example 2: Large Codebase Snapshot Extraction

**Scenario**: Extract relevant code snippets before distributing to code reviewers

**Comonadic Form**: `codebase → extract:relevant → cache:[ast_structure] → compress^3K`

**Implementation**:

```python
@dataclass
class CodebaseContext:
    """Context for large codebases"""
    full_source: dict[str, str]  # {filename: code}
    change_set: list[str]  # Files that changed
    extracted_snippets: Optional[dict] = None
    total_chars: int = 0
    extracted_chars: int = 0

    def __post_init__(self):
        self.total_chars = sum(len(code) for code in self.full_source.values())

    def extract(self, max_chars: int = 3000) -> dict:
        """
        Extract most relevant code snippets

        Strategy:
        1. Include all changed files (highest priority)
        2. Include functions/classes that call changed functions
        3. Include tests for changed code
        4. Cut at token limit
        """
        if self.extracted_snippets:
            return self.extracted_snippets

        relevant_code = {}

        # Priority 1: All changed files
        for filename in self.change_set:
            if filename in self.full_source:
                relevant_code[filename] = self.full_source[filename]

        # Priority 2: Dependencies (files that import changed files)
        dependencies = self._find_dependencies()
        for filename in dependencies:
            if len(str(relevant_code)) < max_chars:
                relevant_code[filename] = self.full_source[filename]

        # Priority 3: Tests
        test_files = [f for f in self.full_source if f.endswith("_test.py")]
        for filename in test_files:
            if len(str(relevant_code)) < max_chars:
                relevant_code[filename] = self.full_source[filename]

        self.extracted_snippets = relevant_code
        self.extracted_chars = sum(len(code) for code in relevant_code.values())

        return relevant_code

    def _find_dependencies(self) -> list[str]:
        """Find files that depend on changed files"""
        # Simplified: parse imports
        dependencies = []
        changed_modules = {f.replace("/", ".").replace(".py", "")
                          for f in self.change_set}

        for filename, code in self.full_source.items():
            if filename not in self.change_set:
                for module in changed_modules:
                    if f"import {module}" in code or f"from {module}" in code:
                        dependencies.append(filename)

        return dependencies

# Usage
def extract_for_review(codebase: CodebaseContext) -> dict:
    """Extract relevant snippets before code review"""
    snippets = codebase.extract(max_chars=3000)

    print(f"Full codebase: {codebase.total_chars:,} chars")
    print(f"Extracted: {codebase.extracted_chars:,} chars")
    print(f"Reduction: {100 * (1 - codebase.extracted_chars/codebase.total_chars):.1f}%")
    print(f"Files included: {len(snippets)}")

    return snippets
```

**Comonadic Perspective**:
- **Extract** intelligently selects changed files + dependencies + tests
- **Cache** preserves which files were extracted (for context)
- **Lazy**: Full codebase never sent to reviewers
- Result: 3K comprehensive snapshot vs 500K full codebase

**Token Cost**:
- Dependency analysis: ~300 tokens
- Review of 3K snapshot: ~1.5K tokens
- Total: ~1.8K tokens (vs 25K+ for full codebase)

---

## Example 3: Research Findings Summary Cache

**Scenario**: Compress research findings into indexed summary before synthesis

**Comonadic Form**: `findings → extract:essence → cache:[citations] → compress^2K`

**Implementation**:

```python
@dataclass
class ResearchContext:
    """Context for research synthesis"""
    raw_findings: list[dict]  # {source, content, relevance}
    working_hypothesis: Optional[str] = None
    summary_index: Optional[dict] = None

    def extract(self, max_chars: int = 2000) -> dict:
        """
        Extract research essence with citation index

        Strategy:
        1. Group by topic cluster
        2. Keep evidence for high-relevance items
        3. Build citation index for references
        4. Create navigation map
        """
        if self.summary_index:
            return self.summary_index

        # Group findings by theme
        themes = self._cluster_findings()

        # For each theme, extract top evidence
        summary = {}
        for theme, findings in themes.items():
            top_findings = sorted(findings,
                                 key=lambda x: x.get("relevance", 0),
                                 reverse=True)[:3]
            summary[theme] = {
                "evidence": [f["content"] for f in top_findings],
                "citations": [f["source"] for f in top_findings],
                "confidence": sum(f.get("relevance", 0.5)
                                for f in top_findings) / len(top_findings)
            }

        # Build navigation map
        self.summary_index = {
            "summary": summary,
            "themes": list(themes.keys()),
            "total_sources": len(set(f["source"] for f in self.raw_findings)),
            "coverage": len(self.raw_findings)
        }

        return self.summary_index

    def _cluster_findings(self) -> dict:
        """Group findings by semantic theme"""
        themes = {}
        for finding in self.raw_findings:
            theme = finding.get("theme", "general")
            if theme not in themes:
                themes[theme] = []
            themes[theme].append(finding)
        return themes

# Usage
def compress_research_before_synthesis(context: ResearchContext) -> dict:
    """Extract research summary before synthesis"""
    summary = context.extract(max_chars=2000)

    print(f"Total findings analyzed: {summary['coverage']}")
    print(f"Unique sources: {summary['total_sources']}")
    print(f"Themes identified: {len(summary['themes'])}")
    print(f"Themes: {', '.join(summary['themes'])}")

    return summary
```

**Why This Is Comonadic**:
1. **Extract**: Pull essence while preserving citations
2. **Compress**: From 50+ finding documents to indexed summary
3. **Cache**: Index enables fast lookup without full decompression
4. **Lazy**: Never load all raw findings unless specifically needed

**Token Cost**:
- Clustering/indexing: ~400 tokens
- Synthesis from summary: ~800 tokens
- Total: ~1.2K tokens (vs 8K+ for full findings)

---

## Composition with Other Patterns

### Pattern 2 + Pattern 3 (Extract + Broadcast)

```
Large context
  ↓ Extract compressed summary (1-2K)
  ↓ Duplicate to multiple agents
  ↓ Each agent works with compressed version (3K per agent, not 30K)
  ↓ Aggregate results
```

**Benefit**: Memory-efficient multi-agent analysis

### Pattern 2 + Pattern 11 (Extract + Streaming)

```
Infinite stream of data
  ↓ Extract window (last N items)
  ↓ Send to aggregation function
  ↓ Cache summary
  ↓ Continue with next window
```

**Benefit**: Process infinite streams within bounded memory

### Pattern 2 + Pattern 5 (Extract + Sequential Pipeline)

```
Raw context
  ↓ Extract for stage 1 (relevant snippets)
  ↓ Pass to agent 1
  ↓ Agent 1 outputs becomes input to Extract for stage 2
  ↓ Different compression strategy per stage
```

**Benefit**: Stage-specific compression optimizes each agent's needs

---

## Compression Strategies Detailed

### Strategy 1: Extractive Summarization
- Keep original sentences/phrases
- Remove redundant sections
- Best for: Preserving exact wording (code, quotes)

### Strategy 2: Abstractive Summarization
- Rephrase using own words
- More aggressive compression
- Best for: Conceptual understanding (research findings)

### Strategy 3: Structural Selection
- Keep structure (headers, sections)
- Remove some content
- Best for: Organized documents (specs, wikis)

### Strategy 4: Semantic Clustering
- Group similar items
- Keep one representative per cluster
- Best for: Deduplication (logs, errors)

---

## Implementation Checklist

- [ ] Define what's "essential" for your domain
- [ ] Choose compression strategy
- [ ] Implement extract() function
- [ ] Add cache mechanism
- [ ] Measure compression ratio
- [ ] Test extraction quality
- [ ] Verify all downstream agents work with compressed version
- [ ] Document token savings
- [ ] Add recovery mechanism (can decompress if needed)

---

## Token Budget Guide

| Scenario | Original | Compressed | Savings |
|----------|----------|-----------|---------|
| Code review (full codebase) | 25K | 3K | 88% |
| Conversation analysis | 8K | 1K | 87% |
| Research synthesis | 12K | 2K | 83% |
| Documentation generation | 15K | 2K | 87% |

**Key Insight**: Extraction typically saves 80-90% of tokens while preserving decision-making information.

---

## Common Pitfalls

**Pitfall 1: Losing critical information**
- Solution: Test with cases where compressed info is critical
- Prevention: Use lossy filter thresholds carefully

**Pitfall 2: Downstream agent needs decompressed**
- Solution: Keep full context cached, decompress as needed
- Prevention: Profile downstream agent needs first

**Pitfall 3: Extraction overhead larger than savings**
- Solution: Cache extracted versions for reuse
- Prevention: Only extract once, before distribution

---

**Mathematical Status**: ✓ Satisfies counit laws (extract ∘ duplicate = id)
**Practical Status**: ✓ Critical for staying within token budgets
**Recommended**: Always use before Pattern #3 (Broadcast)

Created: 2025-10-23
