# Adversarial Pass 2

Suite expanded to **8** attacks; catch_rate **1.0**.

| Attack | Class | Caught |
|--------|-------|--------|
| unknown_agent | registry | yes |
| empty_prompt | validation | yes |
| missing_logic_tag | tags | yes |
| answer_dsl_mismatch | answer↔artifact | yes |
| missing_pseudocode_tag | tags | yes |
| invalid_operator_soup | parse | yes |
| unknown_skill | registry | yes |
| whitespace_only_logic | tags | yes |

## Builder harden next
1. CI job running `attack_suite.py` on every commit.
2. Optional: reject rows where `logic` lacks coding constructs (`fn`/`assert`) — soft gate.
3. Keep firewall: adversarial recipes stay out of blind eval context.
