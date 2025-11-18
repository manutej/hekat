# HEKAT DSL: Archive Plan for Pre-v4.0 Documents

**Date**: 2025-11-01
**Purpose**: Clean separation between current v4.0 architecture and historical documents
**Action**: Move these files to `/Users/manu/Documents/LUXOR/PROJECTS/hekat/docs/archive/pre-v4/`

---

## Archive Structure

```
hekat/docs/archive/
├── pre-v4/                          ← Create this directory
│   ├── architectures/               ← Old architecture documents
│   ├── session-reports/             ← Session summaries
│   ├── research-deep-dives/         ← L6-L7 theoretical deep dives
│   ├── comonadic-explorations/      ← Comonad-specific work
│   └── legacy-specs/                ← Superseded specifications
```

---

## Files to Archive

### 1. OLD ARCHITECTURE DOCUMENTS → `archive/pre-v4/architectures/`

**From**: `/Users/manu/Documents/LUXOR/PROJECTS/hekat/docs/`

```bash
# These are superseded by HEKAT_L1_L7_ARCHITECTURES_BALANCED_v4.0.md

HEKAT_L1_L7_ARCHITECTURES_COMPLETE_v2.0.md
HEKAT_L1_L5_ARCHITECTURES_PRACTICAL_v3.0.md
```

**Reason**: v4.0 is now authoritative. Keep v2.0 and v3.0 for historical reference.

---

### 2. SESSION REPORTS → `archive/pre-v4/session-reports/`

**From**: `/Users/manu/Documents/LUXOR/PROJECTS/hekat/`

```bash
# All session completion summaries

SESSION_2_COMPLETION_SUMMARY.md
SESSION_2B_SUMMARY.md
SESSION_3_COMPLETION_SUMMARY.md
SESSION_4_COMPLETION_SUMMARY.md
SESSION_4_SUMMARY.md
SESSION_5_COMPLETION_SUMMARY.md
COMPILER_INTEGRATION_SUMMARY.md
LEXER_IMPLEMENTATION_SUMMARY.md
```

**Reason**: Historical context, not operational documentation.

---

### 3. L6-L7 RESEARCH DEEP DIVES → `archive/pre-v4/research-deep-dives/`

**From**: `/Users/manu/Documents/LUXOR/PROJECTS/hekat/docs/`

```bash
# Category theory and advanced mathematics (now in research track)

COMONADS-LLM-ORCHESTRATION-ANALYSIS.md
DSL-COMPLEXITY-LEVEL-7.md
LEVEL-7-ARCHITECTURE.md
LEVEL-7-INDEX.md
LEVEL-7-QUICK-REFERENCE.md
LEVEL-7-SUMMARY.md
MARKOV-CATEGORIES-PROBABILISTIC-ORCHESTRATION.md
PROBABILISTIC-HYPERGRAPHS-WORKFLOW-ORCHESTRATION.md
FORMAL-ENCODINGS-SUMMARY.md
FORMAL-SYMBOLIC-ENCODINGS-WORKFLOW-DSLS.md
```

**Reason**: L6-L7 are now research horizons (5-10 years). Keep as reference for future research, but not operational.

---

### 4. COMONADIC-SPECIFIC WORK → `archive/pre-v4/comonadic-explorations/`

**From**: `/Users/manu/Documents/LUXOR/PROJECTS/hekat/docs/`

```bash
# Comonadic DSL variations and beauty references

COMONADIC-COMMAND-BEAUTY-CORRECTED.md
COMONADIC-DSL-COMPLETE-REFERENCE.md
COMMAND-ELEGANCE-INDEX.md
DSL-COMMAND-VARIATIONS.md
DSL-VARIATIONS-VISUAL-MATRIX.md
ELEGANCE-ANALYSIS.md
STACKING-VISUAL-GUIDE.md
```

**Reason**: Beautiful work, but superseded by three-track architecture. Preserve for research reference.

---

### 5. LEGACY SPECIFICATIONS → `archive/pre-v4/legacy-specs/`

**From**: `/Users/manu/Documents/LUXOR/PROJECTS/hekat/docs/`

```bash
# Old complexity level specifications

DSL-COMPLEXITY-LEVELS.md  # Superseded by CORE.md's three-track architecture
```

**From**: `/Users/manu/Documents/LUXOR/PROJECTS/hekat/`

```bash
# Old system specifications

HEKAT_MODE_SYSTEM.md  # Review and possibly keep, but mark as pre-v4
TIER_HOTKEY_REFERENCE.md  # Review and possibly keep, but mark as pre-v4
```

**Reason**: Original 6-level complexity model superseded by L1-L7 three-track architecture.

---

### 6. PROJECT-SPECIFIC SUBDIRECTORIES → Move entire directories

**From**: `/Users/manu/Documents/LUXOR/PROJECTS/hekat/`

```bash
# These are complete subdirectories with their own research

comonad/                 → archive/pre-v4/comonadic-explorations/comonad/
comonad-workflows/       → archive/pre-v4/comonadic-explorations/comonad-workflows/
algebraic-cat/           → archive/pre-v4/research-deep-dives/algebraic-cat/
tmp/                     → DELETE (temporary files)
```

**Reason**: Self-contained research explorations. Preserve for reference but separate from production track.

---

### 7. OLD GUIDES → `archive/pre-v4/legacy-specs/`

**From**: `/Users/manu/Documents/LUXOR/PROJECTS/hekat/docs/`

```bash
DSL-ORCHESTRATION-COMPREHENSIVE.md  # 112KB - comprehensive but pre-three-track
DSL-SYMBOLIC-VISUAL-GUIDE.md
DSL-VERBAL-INTERFACE.md
TUI-ROADMAP.md  # Separate project (LUMINA)
```

**Reason**: Comprehensive documentation pre-dating three-track architecture. Keep for reference.

---

### 8. PDF FILES → `archive/pre-v4/pdfs/`

**From**: `/Users/manu/Documents/LUXOR/PROJECTS/hekat/docs/`

```bash
# All generated PDFs

*.pdf  # Move all to archive/pre-v4/pdfs/
```

**Reason**: PDFs are snapshots of old markdown. Regenerate from v4.0 markdown when needed.

---

## Files to KEEP in Active Directories

### Production Documents (Keep in `/docs/`)

```bash
# Core architecture (v4.0)
HEKAT_L1_L7_ARCHITECTURES_BALANCED_v4.0.md  ← KEEP (authoritative)

# Operational models (refactored)
models/HEKAT_OPERATIONAL_MODEL_v4.md  ← KEEP (newly refactored)
models/HEKAT_QUERY_REFERENCE.md  ← KEEP (to be refactored)
models/HEKAT_MEMORY_MODEL.md  ← KEEP (to be refactored)

# Patterns and guides
patterns/HEKAT_PRACTICAL_PATTERNS.md  ← KEEP (to be refactored)
guides/HEKAT_DSL_STUDY.md  ← KEEP (review and possibly refactor)

# Implementation plans
implementation/HEKAT_PARSER_IMPLEMENTATION_PLAN.md  ← KEEP (to be refactored)

# Integration summary
research/HEKAT_INTEGRATION_SUMMARY.md  ← KEEP (to be refactored)

# Examples
dsl-examples.md  ← KEEP (useful reference)

# Index
INDEX.md  ← KEEP (update to reference v4.0)
PROGRESS.md  ← KEEP (living document)
```

### Root Project Files (Keep in `/hekat/`)

```bash
# Core directives
CORE.md  ← AUTHORITATIVE
README.md  ← Update to reference CORE.md
QUICKSTART.md  ← Update to reference CORE.md

# Implementation files (all keep)
hekat_lexer.py
hekat_parser.py
hekat_compiler.py
hekat_dag_builder.py
hekat_type_checker.py

# Test files (all keep)
test_*.py
run_*.py

# Current summaries
REFACTORING_SUMMARY.md  ← KEEP (current status)
IMPLEMENTATION_ROADMAP.md  ← Review and update
CONSCIOUSNESS_SYSTEM.md  ← Review and update
TASK_RELAY_CONSCIOUSNESS_INTEGRATION.md  ← Review and update

# Living documents
QUERY_BUILDER_SPECIFICATION.md  ← Review and update
PHASE_2_IMPLEMENTATION_GUIDE.md  ← Review and update
```

---

## Bash Commands to Execute Archive

### Step 1: Create Archive Structure

```bash
# Navigate to project
cd /Users/manu/Documents/LUXOR/PROJECTS/hekat/docs

# Create archive directories
mkdir -p archive/pre-v4/architectures
mkdir -p archive/pre-v4/session-reports
mkdir -p archive/pre-v4/research-deep-dives
mkdir -p archive/pre-v4/comonadic-explorations
mkdir -p archive/pre-v4/legacy-specs
mkdir -p archive/pre-v4/pdfs
```

### Step 2: Move Old Architectures

```bash
cd /Users/manu/Documents/LUXOR/PROJECTS/hekat/docs

mv HEKAT_L1_L7_ARCHITECTURES_COMPLETE_v2.0.md archive/pre-v4/architectures/
mv HEKAT_L1_L5_ARCHITECTURES_PRACTICAL_v3.0.md archive/pre-v4/architectures/
```

### Step 3: Move Session Reports

```bash
cd /Users/manu/Documents/LUXOR/PROJECTS/hekat

mv SESSION_2_COMPLETION_SUMMARY.md docs/archive/pre-v4/session-reports/
mv SESSION_2B_SUMMARY.md docs/archive/pre-v4/session-reports/
mv SESSION_3_COMPLETION_SUMMARY.md docs/archive/pre-v4/session-reports/
mv SESSION_4_COMPLETION_SUMMARY.md docs/archive/pre-v4/session-reports/
mv SESSION_4_SUMMARY.md docs/archive/pre-v4/session-reports/
mv SESSION_5_COMPLETION_SUMMARY.md docs/archive/pre-v4/session-reports/
mv COMPILER_INTEGRATION_SUMMARY.md docs/archive/pre-v4/session-reports/
mv LEXER_IMPLEMENTATION_SUMMARY.md docs/archive/pre-v4/session-reports/
```

### Step 4: Move Research Deep Dives

```bash
cd /Users/manu/Documents/LUXOR/PROJECTS/hekat/docs

mv COMONADS-LLM-ORCHESTRATION-ANALYSIS.md archive/pre-v4/research-deep-dives/
mv DSL-COMPLEXITY-LEVEL-7.md archive/pre-v4/research-deep-dives/
mv LEVEL-7-ARCHITECTURE.md archive/pre-v4/research-deep-dives/
mv LEVEL-7-INDEX.md archive/pre-v4/research-deep-dives/
mv LEVEL-7-QUICK-REFERENCE.md archive/pre-v4/research-deep-dives/
mv LEVEL-7-SUMMARY.md archive/pre-v4/research-deep-dives/
mv MARKOV-CATEGORIES-PROBABILISTIC-ORCHESTRATION.md archive/pre-v4/research-deep-dives/
mv PROBABILISTIC-HYPERGRAPHS-WORKFLOW-ORCHESTRATION.md archive/pre-v4/research-deep-dives/
mv FORMAL-ENCODINGS-SUMMARY.md archive/pre-v4/research-deep-dives/
mv FORMAL-SYMBOLIC-ENCODINGS-WORKFLOW-DSLS.md archive/pre-v4/research-deep-dives/
```

### Step 5: Move Comonadic Work

```bash
cd /Users/manu/Documents/LUXOR/PROJECTS/hekat/docs

mv COMONADIC-COMMAND-BEAUTY-CORRECTED.md archive/pre-v4/comonadic-explorations/
mv COMONADIC-DSL-COMPLETE-REFERENCE.md archive/pre-v4/comonadic-explorations/
mv COMMAND-ELEGANCE-INDEX.md archive/pre-v4/comonadic-explorations/
mv DSL-COMMAND-VARIATIONS.md archive/pre-v4/comonadic-explorations/
mv DSL-VARIATIONS-VISUAL-MATRIX.md archive/pre-v4/comonadic-explorations/
mv ELEGANCE-ANALYSIS.md archive/pre-v4/comonadic-explorations/
mv STACKING-VISUAL-GUIDE.md archive/pre-v4/comonadic-explorations/
```

### Step 6: Move Legacy Specs

```bash
cd /Users/manu/Documents/LUXOR/PROJECTS/hekat/docs

mv DSL-COMPLEXITY-LEVELS.md archive/pre-v4/legacy-specs/
mv DSL-ORCHESTRATION-COMPREHENSIVE.md archive/pre-v4/legacy-specs/
mv DSL-SYMBOLIC-VISUAL-GUIDE.md archive/pre-v4/legacy-specs/
mv DSL-VERBAL-INTERFACE.md archive/pre-v4/legacy-specs/
mv TUI-ROADMAP.md archive/pre-v4/legacy-specs/
```

### Step 7: Move Entire Subdirectories

```bash
cd /Users/manu/Documents/LUXOR/PROJECTS/hekat

mv comonad/ docs/archive/pre-v4/comonadic-explorations/comonad/
mv comonad-workflows/ docs/archive/pre-v4/comonadic-explorations/comonad-workflows/
mv algebraic-cat/ docs/archive/pre-v4/research-deep-dives/algebraic-cat/
```

### Step 8: Move PDFs

```bash
cd /Users/manu/Documents/LUXOR/PROJECTS/hekat/docs

mv *.pdf archive/pre-v4/pdfs/
```

### Step 9: Clean Temporary Files

```bash
cd /Users/manu/Documents/LUXOR/PROJECTS/hekat

# Review tmp/ before deleting
ls -la tmp/

# If safe to delete
rm -rf tmp/
```

---

## Verification After Archive

```bash
# Count files in each archive category
find docs/archive/pre-v4/architectures/ -type f | wc -l
find docs/archive/pre-v4/session-reports/ -type f | wc -l
find docs/archive/pre-v4/research-deep-dives/ -type f | wc -l
find docs/archive/pre-v4/comonadic-explorations/ -type f | wc -l
find docs/archive/pre-v4/legacy-specs/ -type f | wc -l
find docs/archive/pre-v4/pdfs/ -type f | wc -l

# List remaining active documents
ls -la docs/
ls -la docs/models/
ls -la docs/patterns/
ls -la docs/implementation/
```

---

## Archive Index (Create This File)

**File**: `/Users/manu/Documents/LUXOR/PROJECTS/hekat/docs/archive/pre-v4/INDEX.md`

```markdown
# Pre-v4.0 Archive Index

**Archived**: 2025-11-01
**Reason**: Superseded by v4.0 Balanced Three-Track Architecture

## What Happened

HEKAT DSL underwent a major architectural refactoring from:
- **Old**: 6-level complexity model with L6-L7 as production features
- **New**: 7-level three-track architecture (Production L1-L4, Experimental L5, Research L6-L7)

**Authoritative Document**: `/Users/manu/Documents/LUXOR/PROJECTS/hekat/CORE.md`

## Archive Contents

### `/architectures/` - Old Architecture Documents
- v2.0: Complete L1-L7 with full category theory
- v3.0: MOE-informed revision (too conservative)

### `/session-reports/` - Development Session Summaries
- Historical context from development sessions
- Implementation progress reports
- Not operational documentation

### `/research-deep-dives/` - L6-L7 Theoretical Work
- Category theory deep dives
- Markov categories, probabilistic hypergraphs
- Formal symbolic encodings
- Now in research track (5-10 year horizon)

### `/comonadic-explorations/` - Comonad-Specific Research
- Comonadic DSL variations
- Command elegance analysis
- Beautiful but superseded by three-track architecture

### `/legacy-specs/` - Superseded Specifications
- Old 6-level complexity model
- Comprehensive orchestration guides
- Pre-three-track documentation

### `/pdfs/` - Generated PDF Snapshots
- PDFs of old markdown files
- Regenerate from v4.0 markdown when needed

## How to Reference

When referencing archived material:
1. Note it's pre-v4.0 architecture
2. Check if concept still applies in three-track model
3. Cite `/CORE.md` for current authoritative guidance

## Preserved for:
- Historical context
- Research reference (L6-L7 future work)
- Understanding evolution of HEKAT DSL
- Category theory foundations
```

---

## Summary

**Total Files to Archive**: ~50+ files
**Archive Location**: `/Users/manu/Documents/LUXOR/PROJECTS/hekat/docs/archive/pre-v4/`
**Time to Execute**: ~5-10 minutes (bash commands)

**Post-Archive Structure**:
```
hekat/
├── CORE.md ⭐ CLEAN ROOT
├── README.md
├── QUICKSTART.md
├── REFACTORING_SUMMARY.md
│
├── docs/
│   ├── HEKAT_L1_L7_ARCHITECTURES_BALANCED_v4.0.md ⭐
│   ├── models/ (refactored v4.0)
│   ├── patterns/ (refactored v4.0)
│   ├── implementation/ (refactored v4.0)
│   └── archive/
│       └── pre-v4/ (all old content)
│
└── [implementation files remain unchanged]
```

---

**Next Step**: Execute archive bash commands, then proceed with document refactoring.
