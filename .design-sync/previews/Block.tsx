import { Block, Figure } from '@hekat/figtree-ds';

/** The four tones of the teaching palette, each with a family icon. */
export const Tones = () => (
  <Figure width={640} height={96} preset="teaching" id="blk-tones">
    <Block id="t-attention" x={24} y={24} width={136} height={48} label="Attention" tone="attention" icon="search" />
    <Block id="t-processing" x={184} y={24} width={136} height={48} label="Processing" tone="processing" icon="gear" />
    <Block id="t-residual" x={344} y={24} width={136} height={48} label="Residual" tone="residual" icon="residual" />
    <Block id="t-input" x={504} y={24} width={112} height={48} label="Input" tone="input" icon="document" />
  </Figure>
);

/** The element vocabulary: store, document, decision, terminal, actor and process beside a plain block. */
export const Kinds = () => (
  <Figure width={720} height={120} preset="teaching" id="blk-kinds">
    <Block id="k-block" x={16} y={32} width={96} height={48} label="Block" />
    <Block id="k-store" x={128} y={24} width={96} height={64} label="Store" kind="store" tone="input" />
    <Block id="k-doc" x={240} y={32} width={96} height={48} label="Document" kind="document" tone="residual" />
    <Block id="k-decision" x={352} y={24} width={112} height={64} label="Check?" kind="decision" tone="attention" />
    <Block id="k-terminal" x={480} y={32} width={96} height={48} label="Start" kind="terminal" tone="input" />
    <Block id="k-actor" x={592} y={16} width={48} height={56} label="Reader" kind="actor" />
    <Block id="k-process" x={656} y={32} width={56} height={48} label="Run" kind="process" />
  </Figure>
);

/** A block with a second annotation line, in the paper register. */
export const WithNote = () => (
  <Figure width={320} height={96} preset="paper" id="blk-note">
    <Block id="n-1" x={24} y={24} width={272} height={48} label="Critic" note="dual-space review, ≤ 3 rounds" preset="paper" tone="attention" icon="critic" />
  </Figure>
);
