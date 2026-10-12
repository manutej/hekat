import type { IconName } from './icons.generated';
import { shapePath, textInset, type Kind } from './shapes';
import { PRESETS, type PresetName, type Tone } from './tokens';

export interface BlockProps {
  id: string;
  x: number;
  y: number;
  width: number;
  height: number;
  /** The label, centred; keep it to a few words so it fits at the preset's label size. */
  label: string;
  /** Element vocabulary: block, store (cylinder), document, decision (diamond), terminal (pill), actor, process. */
  kind?: Kind;
  /** Fill tone: attention, processing, residual or input. */
  tone?: Tone;
  /** Family icon drawn at the left of the label. */
  icon?: IconName;
  /** Preset used for stroke, radius and type; normally the parent <Figure>'s. */
  preset?: PresetName;
  /** Optional second line set in the annotation size under the label. */
  note?: string;
}

/**
 * A leaf of the layout tree: one shape, one label, optionally one icon. The shape carries
 * `data-role="block"` whatever its kind, so the critic, the ports and the editor treat a
 * cylinder exactly like a rectangle of the same bbox.
 */
export function Block({ id, x, y, width, height, label, kind = 'block', tone = 'processing', icon, preset = 'teaching', note }: BlockProps) {
  const p = PRESETS[preset];
  const [insetL, insetR] = textInset(kind);
  const iconSize = Math.min(24, Math.max(16, Math.round(height / 2.5)));
  const hasIcon = Boolean(icon);
  const labelX = hasIcon ? x + insetL + 12 + iconSize + 8 : x + insetL + (width - insetL - insetR) / 2;
  const labelY = note ? y + height / 2 - p.fontSize.annot / 2 + p.fontSize.label * 0.35 : y + height / 2 + p.fontSize.label * 0.35;
  const shape =
    kind === 'block' ? (
      <rect
        id={`${id}-shape`}
        x={x}
        y={y}
        width={width}
        height={height}
        rx={p.radius.block}
        fill={p.palette[tone]}
        stroke={p.palette.border}
        strokeWidth={p.stroke.border}
        data-role="block"
        data-kind={kind}
      />
    ) : (
      <path
        id={`${id}-shape`}
        d={shapePath(kind, width, height)}
        transform={`translate(${x},${y})`}
        fill={kind === 'actor' ? 'none' : p.palette[tone]}
        stroke={p.palette.border}
        strokeWidth={kind === 'actor' ? p.stroke.main : p.stroke.border}
        strokeLinejoin="round"
        data-role="block"
        data-kind={kind}
      />
    );
  return (
    <g id={id} data-role="leaf" data-bbox={`${x} ${y} ${width} ${height}`} data-tone={tone}>
      {shape}
      {hasIcon ? (
        <use
          id={`${id}-icon`}
          href={`#icon-${icon}`}
          x={x + insetL + 12}
          y={y + (height - iconSize) / 2}
          width={iconSize}
          height={iconSize}
          color={p.palette.icon}
          data-role="icon"
        />
      ) : null}
      <text
        id={`${id}-label`}
        x={labelX}
        y={kind === 'actor' ? y + height + p.fontSize.label : labelY}
        textAnchor={hasIcon ? 'start' : 'middle'}
        fontSize={p.fontSize.label}
        fill={p.palette.label}
        data-role="label"
      >
        {label}
      </text>
      {note ? (
        <text
          id={`${id}-note`}
          x={labelX}
          y={labelY + p.fontSize.annot + 2}
          textAnchor={hasIcon ? 'start' : 'middle'}
          fontSize={p.fontSize.annot}
          fill={p.palette.title}
          data-role="annotation"
        >
          {note}
        </text>
      ) : null}
    </g>
  );
}
