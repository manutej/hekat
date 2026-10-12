import { MARKER_ID } from './Figure';
import { PRESETS, type PresetName } from './tokens';

export type FlowType = 'data' | 'control' | 'feedback';

export interface FlowProps {
  id: string;
  /** Right-angle polyline in figure coordinates; the final segment should be at least the preset's minArrow. */
  points: Array<[number, number]>;
  /** data (solid, ink), control (dashed, grey), feedback (dashed, ink). */
  type?: FlowType;
  /** Source and target element ids, kept as data attributes for the critic and the animation layer. */
  from?: string;
  to?: string;
  /** Short label set beside the longest segment. */
  label?: string;
  preset?: PresetName;
  /** Draw without the arrowhead (a plain connector). */
  noHead?: boolean;
}

/**
 * A connection between two blocks: a right-angle path with an arrowhead marker. The flow type
 * is what the motion grammar binds to (data flows pulse, control flows pulse slower and dimmer),
 * so set it from meaning, not from looks.
 */
export function Flow({ id, points, type = 'data', from, to, label, preset = 'teaching', noHead }: FlowProps) {
  const p = PRESETS[preset];
  const d = points.map(([x, y], i) => `${i === 0 ? 'M' : 'L'}${x},${y}`).join(' ');
  const dashed = type !== 'data';
  const stroke = type === 'control' ? p.palette.control : p.palette.border;
  let lx = 0, ly = 0, best = -1;
  for (let i = 1; i < points.length; i++) {
    const [ax, ay] = points[i - 1];
    const [bx, by] = points[i];
    const len = Math.abs(bx - ax) + Math.abs(by - ay);
    if (len > best) { best = len; lx = (ax + bx) / 2; ly = (ay + by) / 2 - 6; }
  }
  return (
    <g id={id} data-role="flow-group">
      <path
        id={`${id}-path`}
        d={d}
        fill="none"
        stroke={stroke}
        strokeWidth={p.stroke.main}
        strokeDasharray={dashed ? '6 4' : undefined}
        markerEnd={noHead ? undefined : `url(#${MARKER_ID})`}
        data-role="flow"
        data-flow={type}
        data-from={from}
        data-to={to}
      />
      {label ? (
        <text id={`${id}-label`} x={lx} y={ly} textAnchor="middle" fontSize={p.fontSize.annot} fill={p.palette.title} data-role="annotation">
          {label}
        </text>
      ) : null}
    </g>
  );
}
