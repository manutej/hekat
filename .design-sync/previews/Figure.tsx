import { Block, Caption, Container, Figure, Flow } from '@hekat/figtree-ds';

/** The FigTree self-application figure in the teaching preset: the loop that built this design system. */
export const TeachingFigure = () => (
  <div>
    <Figure width={720} height={256} preset="teaching" title="FigTree loop" id="fig-teaching">
      <Container id="c-ground" x={24} y={24} width={168} height={96} title="Grounding">
        <Block id="grounder" x={40} y={56} width={136} height={48} label="Grounder" icon="grounder" tone="attention" />
      </Container>
      <Container id="c-build" x={232} y={24} width={288} height={200} title="Recursive construction">
        <Block id="generator" x={248} y={56} width={112} height={48} label="Generator" icon="tree" />
        <Block id="decompose" x={392} y={56} width={120} height={48} label="Decompose" icon="decompose" />
        <Block id="merge" x={248} y={152} width={112} height={48} label="Merge" icon="merge" tone="input" />
        <Block id="draw" x={392} y={152} width={120} height={48} label="Draw" icon="draw-leaf" tone="input" />
        <Flow id="f-gen-dec" from="generator" to="decompose" points={[[360, 80], [392, 80]]} />
        <Flow id="f-dec-draw" from="decompose" to="draw" points={[[452, 104], [452, 152]]} />
        <Flow id="f-draw-merge" from="draw" to="merge" points={[[392, 176], [360, 176]]} />
      </Container>
      <Container id="c-review" x={544} y={24} width={160} height={200} title="Review">
        <Block id="critic" x={568} y={56} width={120} height={48} label="Critic" icon="critic" tone="residual" />
        <Block id="worker" x={568} y={152} width={120} height={48} label="Worker" icon="repair" />
        <Flow id="f-critic-worker" from="critic" to="worker" points={[[600, 104], [600, 152]]} />
        <Flow id="f-worker-critic" from="worker" to="critic" type="control" points={[[656, 152], [656, 104]]} />
      </Container>
      <Flow id="f-ground-gen" from="grounder" to="generator" points={[[176, 80], [248, 80]]} label="content plan" />
      <Flow id="f-merge-worker" from="merge" to="worker" points={[[304, 200], [304, 240], [628, 240], [628, 200]]} />
    </Figure>
    <Caption lead="Figure 1." preset="teaching" width={720}>
      The Grounder admits only evidenced components; the Generator decomposes and draws; the Critic reviews the
      render in code and image, and the Worker repairs with local edits.
    </Caption>
  </div>
);

/** The same mechanism in the paper preset: Times, flat fills, dashed containers, 12 px labels. */
export const PaperFigure = () => (
  <Figure width={560} height={176} preset="paper" title="Pipeline (paper register)" id="fig-paper">
    <Container id="p-c1" x={24} y={24} width={512} height={128} title="Render–critic loop" preset="paper">
      <Block id="p-render" x={48} y={72} width={112} height={40} label="Render" preset="paper" tone="input" />
      <Block id="p-critic" x={224} y={72} width={112} height={40} label="Critic" preset="paper" tone="attention" />
      <Block id="p-worker" x={400} y={72} width={112} height={40} label="Worker" preset="paper" tone="processing" />
      <Flow id="p-f1" from="p-render" to="p-critic" points={[[160, 92], [224, 92]]} preset="paper" />
      <Flow id="p-f2" from="p-critic" to="p-worker" points={[[336, 92], [400, 92]]} preset="paper" />
      <Flow id="p-f3" from="p-worker" to="p-render" type="control" points={[[456, 112], [456, 136], [104, 136], [104, 112]]} preset="paper" />
    </Container>
  </Figure>
);

/** Slide preset: projector-scale labels, wider gaps, larger arrowheads. */
export const SlideFigure = () => (
  <Figure width={720} height={160} preset="slide" title="Three steps (slide register)" id="fig-slide">
    <Block id="s-1" x={40} y={48} width={176} height={64} label="Ground" icon="grounder" preset="slide" tone="attention" />
    <Block id="s-2" x={272} y={48} width={176} height={64} label="Construct" icon="tree" preset="slide" />
    <Block id="s-3" x={504} y={48} width={176} height={64} label="Refine" icon="loop" preset="slide" tone="residual" />
    <Flow id="s-f1" from="s-1" to="s-2" points={[[216, 80], [272, 80]]} preset="slide" />
    <Flow id="s-f2" from="s-2" to="s-3" points={[[448, 80], [504, 80]]} preset="slide" />
  </Figure>
);
