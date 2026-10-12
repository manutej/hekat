import { Block, Figure, Flow } from '@hekat/figtree-ds';

/** Data flow: solid ink with an arrowhead, labelled on its longest segment. */
export const Data = () => (
  <Figure width={400} height={96} preset="teaching" id="flow-data">
    <Block id="fd-a" x={24} y={24} width={120} height={48} label="Grounder" icon="grounder" tone="attention" />
    <Block id="fd-b" x={256} y={24} width={120} height={48} label="Generator" icon="tree" />
    <Flow id="fd-f" from="fd-a" to="fd-b" points={[[144, 48], [256, 48]]} label="content plan" />
  </Figure>
);

/** Control flow: dashed grey, routed at right angles back to an earlier block. */
export const Control = () => (
  <Figure width={400} height={128} preset="teaching" id="flow-control">
    <Block id="fc-a" x={24} y={24} width={120} height={48} label="Critic" icon="critic" tone="residual" />
    <Block id="fc-b" x={256} y={24} width={120} height={48} label="Worker" icon="repair" />
    <Flow id="fc-f1" from="fc-a" to="fc-b" points={[[144, 48], [256, 48]]} />
    <Flow id="fc-f2" from="fc-b" to="fc-a" type="control" points={[[316, 72], [316, 104], [84, 104], [84, 72]]} label="re-validate" />
  </Figure>
);

/** Feedback flow (dashed ink) and a headless connector. */
export const FeedbackAndConnector = () => (
  <Figure width={400} height={128} preset="teaching" id="flow-feedback">
    <Block id="ff-a" x={24} y={24} width={120} height={48} label="Render" icon="render" tone="input" />
    <Block id="ff-b" x={256} y={24} width={120} height={48} label="Critic" icon="critic" tone="residual" />
    <Flow id="ff-f1" from="ff-a" to="ff-b" type="feedback" points={[[144, 48], [256, 48]]} />
    <Flow id="ff-f2" from="ff-a" to="ff-b" points={[[84, 72], [84, 104], [316, 104], [316, 72]]} noHead />
  </Figure>
);
