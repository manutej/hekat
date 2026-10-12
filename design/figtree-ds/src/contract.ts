/**
 * The generative-UI contract (mirror of design/contract/figure-program.schema.json).
 *
 * A FigureProgram is design-free: ids, boxes, kinds, tones, icons and flow types. A
 * DesignAdapter turns it into React; swapping the design means supplying another adapter and
 * nothing upstream (grounder, worker, critic, edit scripts) changes, because every id survives.
 */
import type { ReactNode } from 'react';
import type { IconName } from './icons.generated';
import type { Kind } from './shapes';
import type { PresetName, Tone } from './tokens';

export type FlowType = 'data' | 'control' | 'conditional' | 'feedback';

export interface BBox { x: number; y: number; w: number; h: number }
export type Point = [number, number];

export interface ProgramCanvas { width: number; height: number; preset?: PresetName | string; grid?: number }

export interface ProgramContainer {
  id: string;
  title?: string;
  bbox: BBox;
  parent?: string;
  depth?: number;
  /** false for a layout group the worker did not box; a design may still show it. */
  boxed?: boolean;
}

export interface ProgramNode {
  id: string;
  label: string;
  bbox: BBox;
  kind?: Kind;
  tone?: Tone;
  icon?: IconName | string;
  note?: string;
  parent?: string;
  evidence_span?: string;
}

export interface ProgramFlow {
  id: string;
  from: string;
  to: string;
  type?: FlowType;
  points: Point[];
  label?: string;
  head?: boolean;
  evidence_span?: string;
}

export interface ProgramPort { id: string; side: 'left' | 'right' | 'top' | 'bottom'; x: number; y: number; type?: 'input' | 'output'; component?: string }
export interface ProgramResidual { severity: 'critical' | 'warning' | 'info'; description: string; anchor?: string }

export interface FigureProgram {
  version: 1;
  title?: string;
  source?: string;
  canvas: ProgramCanvas;
  containers?: ProgramContainer[];
  nodes: ProgramNode[];
  flows: ProgramFlow[];
  ports?: ProgramPort[];
  caption?: { lead?: string; text?: string };
  residuals?: ProgramResidual[];
  meta?: Record<string, unknown>;
}

/** What a design must provide to render a program. Every element keeps the program's id. */
export interface DesignAdapter {
  /** The canvas: background, defs (marker, icon symbols), tokens. Children are the rendered parts. */
  figure(program: FigureProgram, children: ReactNode): ReactNode;
  container(c: ProgramContainer, program: FigureProgram): ReactNode;
  node(n: ProgramNode, program: FigureProgram): ReactNode;
  flow(f: ProgramFlow, program: FigureProgram): ReactNode;
  /** Optional caption rendered outside the SVG. */
  caption?(c: NonNullable<FigureProgram['caption']>, program: FigureProgram): ReactNode;
}

/** Structural problems a program may have beyond the JSON schema. */
export function validateProgram(p: FigureProgram): string[] {
  const problems: string[] = [];
  if (p.version !== 1) problems.push('version must be 1');
  const ids = new Set<string>();
  for (const el of [...(p.containers ?? []), ...p.nodes]) {
    if (ids.has(el.id)) problems.push(`duplicate id ${el.id}`);
    ids.add(el.id);
  }
  for (const f of p.flows) {
    if (f.points.length < 2) problems.push(`flow ${f.id}: fewer than two points`);
    for (const end of ['from', 'to'] as const) {
      if (!ids.has(f[end]) && f[end] !== 'unknown') problems.push(`flow ${f.id}: ${end} ${f[end]} is not an element id`);
    }
  }
  for (const n of p.nodes) if (n.parent && !ids.has(n.parent)) problems.push(`node ${n.id}: parent ${n.parent} unknown`);
  return problems;
}
