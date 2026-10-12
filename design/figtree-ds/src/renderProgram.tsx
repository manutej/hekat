import type { ReactNode } from 'react';
import { Block } from './Block';
import { Caption } from './Caption';
import { Container } from './Container';
import { Figure } from './Figure';
import { Flow } from './Flow';
import { ICON_PATHS, type IconName } from './icons.generated';
import type { DesignAdapter, FigureProgram, ProgramContainer, ProgramFlow, ProgramNode } from './contract';
import type { PresetName } from './tokens';

const presetOf = (p: FigureProgram): PresetName =>
  p.canvas.preset === 'paper' || p.canvas.preset === 'slide' ? p.canvas.preset : 'teaching';

/** The house design: the FigTree components under the program's preset. */
export const houseAdapter: DesignAdapter = {
  figure(p, children) {
    return (
      <Figure id={p.nodes.length ? 'figure' : 'figure-empty'} width={p.canvas.width} height={p.canvas.height} preset={presetOf(p)} title={p.title}>
        {children}
      </Figure>
    );
  },
  container(c: ProgramContainer, p) {
    if (c.boxed === false) return null;
    return <Container key={c.id} id={c.id} x={c.bbox.x} y={c.bbox.y} width={c.bbox.w} height={c.bbox.h} title={c.title} preset={presetOf(p)} />;
  },
  node(n: ProgramNode, p) {
    const icon = n.icon && n.icon in ICON_PATHS ? (n.icon as IconName) : undefined;
    return (
      <Block key={n.id} id={n.id} x={n.bbox.x} y={n.bbox.y} width={n.bbox.w} height={n.bbox.h} label={n.label} kind={n.kind} tone={n.tone} icon={icon} note={n.note} preset={presetOf(p)} />
    );
  },
  flow(f: ProgramFlow, p) {
    const type = f.type === 'conditional' ? 'control' : f.type ?? 'data';
    return <Flow key={f.id} id={f.id} points={f.points} type={type} from={f.from} to={f.to} label={f.label} noHead={f.head === false} preset={presetOf(p)} />;
  },
  caption(c, p) {
    return <Caption lead={c.lead} preset={presetOf(p)} width={p.canvas.width}>{c.text}</Caption>;
  },
};

/**
 * Render a FigureProgram through a design. Containers outer to inner, then nodes, then flows,
 * so arrows always sit on top; the caption (if any) follows the SVG.
 */
export function renderProgram(program: FigureProgram, adapter: DesignAdapter = houseAdapter): ReactNode {
  const containers = [...(program.containers ?? [])].sort((a, b) => (a.depth ?? 0) - (b.depth ?? 0));
  const body = (
    <>
      {containers.map((c) => adapter.container(c, program))}
      {program.nodes.map((n) => adapter.node(n, program))}
      {program.flows.map((f) => adapter.flow(f, program))}
    </>
  );
  const fig = adapter.figure(program, body);
  if (program.caption && adapter.caption) {
    return (
      <div data-program-id={program.title ?? 'figure'}>
        {fig}
        {adapter.caption(program.caption, program)}
      </div>
    );
  }
  return fig;
}

export interface ProgramViewProps { program: FigureProgram; adapter?: DesignAdapter }

/** Component form of renderProgram, for JSX use and for the design-system preview. */
export function ProgramView({ program, adapter }: ProgramViewProps) {
  return <>{renderProgram(program, adapter)}</>;
}
