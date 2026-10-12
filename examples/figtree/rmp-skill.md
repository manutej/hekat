# Recursive Meta Prompting (RMP) Skill

Turn a one-line task into a converged meta-prompt by repeatedly generating, critiquing and
refining a typed prompt scaffold until adversarial review returns no critical defects.

## Workflow

1. **Task Intake**: read the task statement and extract the category of problems it belongs to
2. **Slot Typing**: name the typed slots (inputs, constraints, outputs) the meta-prompt must expose
3. **Scaffold Draft**: write the first meta-prompt as a how-to-think scaffold without worked examples
4. **Adversarial Review**: eight review agents attack the draft for faithfulness, hallucination and completeness
5. **Refine Step**: apply only the anchored fixes from the review to the scaffold
6. **Convergence Check**: stop when two successive reviews return no critical defects

The refine loop is explicit: Adversarial Review → Refine Step → Convergence Check → repeat until converged.

## Data flow

Task Intake → Slot Typing → Scaffold Draft → Adversarial Review

Input: task statement
Output: converged meta-prompt, residual defect list
