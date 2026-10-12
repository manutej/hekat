import type { CSSProperties, SVGProps } from 'react';
import { ICON_PATHS, ICON_VIEWBOX, type IconName } from './icons.generated';

export interface IconProps extends Omit<SVGProps<SVGSVGElement>, 'name'> {
  /** Icon from the FigTree family (24x24 grid, 2 px monoline, currentColor). */
  name: IconName;
  /** Rendered size in px; the family is designed to read at 16, 24 and 48. */
  size?: number;
  /** Accessible label; omit for a purely decorative icon. */
  title?: string;
  style?: CSSProperties;
}

/**
 * A FigTree family icon. Inherits `color` for its stroke, so it follows the ink of its
 * surroundings in light and dark themes alike. Use inside a <Block> via its `icon` prop,
 * or standalone in legends, headings and tiles.
 */
export function Icon({ name, size = 24, title, style, ...rest }: IconProps) {
  const inner = ICON_PATHS[name];
  return (
    <svg
      width={size}
      height={size}
      viewBox={ICON_VIEWBOX}
      fill="none"
      stroke="currentColor"
      strokeWidth={2}
      strokeLinecap="round"
      strokeLinejoin="round"
      role={title ? 'img' : undefined}
      aria-hidden={title ? undefined : true}
      data-icon={name}
      style={{ display: 'inline-block', verticalAlign: 'middle', flexShrink: 0, ...style }}
      {...rest}
    >
      {title ? <title>{title}</title> : null}
      <g dangerouslySetInnerHTML={{ __html: inner }} />
    </svg>
  );
}
