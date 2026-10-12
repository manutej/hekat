import { Block, Caption, Figure, Flow } from '@hekat/figtree-ds';

/** A numbered caption under a small figure. */
export const UnderFigure = () => (
  <div>
    <Figure width={400} height={96} preset="teaching" id="cap-fig">
      <Block id="cap-a" x={24} y={24} width={120} height={48} label="Source" icon="document" tone="input" />
      <Block id="cap-b" x={256} y={24} width={120} height={48} label="Figure" icon="image" />
      <Flow id="cap-f" from="cap-a" to="cap-b" points={[[144, 48], [256, 48]]} />
    </Figure>
    <Caption lead="Figure 3." preset="teaching" width={400}>
      Only components with an evidence span in the source are drawn; everything else is logged as a residual.
    </Caption>
  </div>
);

/** Caption without a lead, in the paper register. */
export const Plain = () => (
  <Caption preset="paper" width={360}>
    Arrow shafts are at least 20 px long; targets move, endpoints never do.
  </Caption>
);

/** Slide register: larger type for a projected caption. */
export const Slide = () => (
  <Caption lead="Takeaway" preset="slide" width={520}>
    Critique in two spaces: the code and the rendered image.
  </Caption>
);
