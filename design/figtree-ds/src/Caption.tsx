import type { CSSProperties, ReactNode } from 'react';
import type { PresetName } from './tokens';

export interface CaptionProps {
  /** Figure number or short bold lead, e.g. "Figure 2." */
  lead?: string;
  children: ReactNode;
  preset?: PresetName;
  /** Width to wrap at; defaults to the figure width when placed under a <Figure>. */
  width?: number;
  style?: CSSProperties;
}

/**
 * The caption under a figure: a bold lead and a sentence that says what the reader should see.
 * Rendered as HTML (not inside the SVG) so it reflows with the page.
 */
export function Caption({ lead, children, preset = 'teaching', width, style }: CaptionProps) {
  return (
    <p className="ft-caption" data-preset={preset} style={{ maxWidth: width, ...style }}>
      {lead ? <b>{lead} </b> : null}
      {children}
    </p>
  );
}
