import type { CSSProperties, ReactNode } from 'react';
import { ICON_PATHS, ICON_VIEWBOX, type IconName } from './icons.generated';
import { PRESETS, type PresetName } from './tokens';

export interface FigureProps {
  /** Canvas width in px (multiple of the 8 px grid). */
  width: number;
  /** Canvas height in px (multiple of the 8 px grid). */
  height: number;
  /** Style preset: `paper` (academic), `teaching` (editorial) or `slide` (projector scale). */
  preset?: PresetName;
  /** Accessible title written as the SVG <title>. */
  title?: string;
  /** Element id of the root <svg>; children ids should be stable so edits stay local. */
  id?: string;
  /** Icons to define as <symbol>s; by default every family icon used by a <Block> is defined. */
  icons?: IconName[];
  /** Figure content: <Container>, <Block>, <Flow>. */
  children?: ReactNode;
  className?: string;
  style?: CSSProperties;
}

export const MARKER_ID = 'ft-arrow';

/**
 * The canvas every FigTree figure lives on: a white background drawn first, arrowhead marker
 * and icon symbols in <defs>, and the preset's tokens applied through CSS variables. The
 * figure is an addressable program: give every child a stable id and the critic, the editor
 * and the animation layer can all find it.
 */
export function Figure({ width, height, preset = 'teaching', title, id = 'figure', icons, children, className, style }: FigureProps) {
  const p = PRESETS[preset];
  const names = icons ?? (Object.keys(ICON_PATHS) as IconName[]);
  return (
    <svg
      id={id}
      xmlns="http://www.w3.org/2000/svg"
      width={width}
      height={height}
      viewBox={`0 0 ${width} ${height}`}
      className={['ft-figure', className].filter(Boolean).join(' ')}
      data-preset={preset}
      data-figtree="1"
      fontFamily={p.font}
      style={{ background: '#fff', ...style }}
    >
      {title ? <title>{title}</title> : null}
      <rect id={`${id}-background`} x={0} y={0} width={width} height={height} fill="#FFFFFF" data-role="background" />
      <defs>
        <marker
          id={MARKER_ID}
          markerWidth={p.marker.w}
          markerHeight={p.marker.h}
          refX={p.marker.w}
          refY={p.marker.h / 2}
          orient="auto"
          markerUnits="userSpaceOnUse"
        >
          <path d={`M0,0 L${p.marker.w},${p.marker.h / 2} L0,${p.marker.h} z`} fill={p.palette.border} />
        </marker>
        {names.map((n) => (
          <symbol
            key={n}
            id={`icon-${n}`}
            viewBox={ICON_VIEWBOX}
            fill="none"
            stroke="currentColor"
            strokeWidth={2}
            strokeLinecap="round"
            strokeLinejoin="round"
            dangerouslySetInnerHTML={{ __html: ICON_PATHS[n] }}
          />
        ))}
      </defs>
      <g id={`${id}-content`} data-bbox={`0 0 ${width} ${height}`}>
        {children}
      </g>
    </svg>
  );
}
