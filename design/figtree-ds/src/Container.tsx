import type { ReactNode } from 'react';
import { PRESETS, type PresetName } from './tokens';

export interface ContainerProps {
  id: string;
  x: number;
  y: number;
  width: number;
  height: number;
  /** Title set in the top-left corner; omit for an untitled grouping box. */
  title?: string;
  /** Preset used for stroke, dash and radius; normally the parent <Figure>'s. */
  preset?: PresetName;
  /** Children positioned in figure coordinates (not relative to the container). */
  children?: ReactNode;
}

/**
 * A grouping box around a sub-figure: a node of the layout tree. Blocks inside keep their
 * figure coordinates so an arrow that crosses the boundary is still one straight edit.
 */
export function Container({ id, x, y, width, height, title, preset = 'teaching', children }: ContainerProps) {
  const p = PRESETS[preset];
  return (
    <g id={id} data-role="container" data-bbox={`${x} ${y} ${width} ${height}`}>
      <rect
        id={`${id}-box`}
        x={x}
        y={y}
        width={width}
        height={height}
        rx={p.radius.container}
        fill={p.palette.container}
        stroke={preset === 'paper' ? p.palette.border : '#D5DBE4'}
        strokeWidth={p.stroke.border}
        strokeDasharray={p.containerDash || undefined}
      />
      {title ? (
        <text
          id={`${id}-title`}
          x={x + 12}
          y={y + 8 + p.fontSize.title}
          fontSize={p.fontSize.title}
          fontWeight={preset === 'paper' ? 'normal' : 600}
          fill={p.palette.title}
          data-role="title"
        >
          {title}
        </text>
      ) : null}
      {children}
    </g>
  );
}
