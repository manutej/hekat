import { Block, Container, Figure, Flow } from '@hekat/figtree-ds';

/** A titled container holding two blocks and the flow between them. */
export const Titled = () => (
  <Figure width={400} height={128} preset="teaching" id="ctr-titled">
    <Container id="ct-1" x={24} y={24} width={352} height={80} title="Recursive construction">
      <Block id="ct-a" x={40} y={48} width={136} height={40} label="Decompose" icon="decompose" />
      <Block id="ct-b" x={224} y={48} width={136} height={40} label="Draw" icon="draw-leaf" tone="input" />
      <Flow id="ct-f" from="ct-a" to="ct-b" points={[[176, 68], [224, 68]]} />
    </Container>
  </Figure>
);

/** Nested containers: one level of the layout tree inside another. */
export const Nested = () => (
  <Figure width={480} height={176} preset="teaching" id="ctr-nested">
    <Container id="cn-outer" x={24} y={24} width={432} height={128} title="Review">
      <Container id="cn-inner" x={40} y={56} width={224} height={80} title="Critic">
        <Block id="cn-code" x={56} y={80} width={88} height={40} label="Code" tone="input" />
        <Block id="cn-image" x={160} y={80} width={88} height={40} label="Image" tone="input" />
      </Container>
      <Block id="cn-worker" x={304} y={80} width={128} height={40} label="Worker" icon="repair" />
      <Flow id="cn-f" from="cn-inner" to="cn-worker" points={[[264, 100], [304, 100]]} />
    </Container>
  </Figure>
);

/** Untitled dashed container in the paper register. */
export const Paper = () => (
  <Figure width={320} height={112} preset="paper" id="ctr-paper">
    <Container id="cp-1" x={24} y={24} width={272} height={64} preset="paper">
      <Block id="cp-a" x={40} y={40} width={104} height={32} label="Parse" preset="paper" />
      <Block id="cp-b" x={176} y={40} width={104} height={32} label="Validate" preset="paper" tone="attention" />
      <Flow id="cp-f" from="cp-a" to="cp-b" points={[[144, 56], [176, 56]]} preset="paper" />
    </Container>
  </Figure>
);
