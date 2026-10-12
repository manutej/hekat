import { ProgramView, houseAdapter, type DesignAdapter } from '@hekat/figtree-ds';
import { figtreeLoop } from './figtree-loop.program';

/** The generative-UI contract at work: a FigureProgram exported from the pipeline, rendered by the house design. */
export const HouseDesign = () => <ProgramView program={figtreeLoop} />;

/** The same program under the paper preset: nothing upstream changed, only the design. */
export const PaperDesign = () => <ProgramView program={{ ...figtreeLoop, canvas: { ...figtreeLoop.canvas, preset: 'paper' } }} />;

/** A swapped adapter: every node becomes an attention-toned block with an upper-case label; ids survive, so edit scripts still apply. */
const loudAdapter: DesignAdapter = {
  ...houseAdapter,
  node: (n, p) => houseAdapter.node({ ...n, label: n.label.toUpperCase(), tone: 'attention', icon: undefined }, p),
};
export const SwappedDesign = () => <ProgramView program={figtreeLoop} adapter={loudAdapter} />;
