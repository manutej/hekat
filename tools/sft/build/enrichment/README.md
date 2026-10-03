# Composer enrichment drops

Agents write `batch_*.jsonl` here. Merge with:

```bash
python3 tools/sft/build/enrich_from_agent_jsonl.py tools/sft/build/enrichment/batch_a.jsonl
# or cat batches first
cat tools/sft/build/enrichment/batch_*.jsonl > tools/sft/build/enrichment/all.jsonl
python3 tools/sft/build/enrich_from_agent_jsonl.py tools/sft/build/enrichment/all.jsonl
```

Then re-run validate + blind eval + monitor.
