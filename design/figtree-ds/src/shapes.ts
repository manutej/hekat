/** Leaf element vocabulary, ported from figtree/elements.py: one path per kind. */
export type Kind = 'block' | 'store' | 'document' | 'decision' | 'terminal' | 'actor' | 'process';
export const KINDS: Kind[] = ['block', 'store', 'document', 'decision', 'terminal', 'actor', 'process'];

const g = (n: number): string => (Number.isInteger(n) ? String(n) : String(Number(n.toFixed(2))));

/** Path data (origin top-left) for a block of `kind` filling a w x h bbox. */
export function shapePath(kind: Kind, w: number, h: number): string {
  if (kind === 'store') {
    const ry = Math.max(4, Math.floor(h / 6));
    return `M0,${ry} A${g(w / 2)},${ry} 0 0 1 ${w},${ry} V${h - ry} A${g(w / 2)},${ry} 0 0 1 0,${h - ry} Z M0,${ry} A${g(w / 2)},${ry} 0 0 0 ${w},${ry}`;
  }
  if (kind === 'document') {
    const c = 8;
    return `M0,0 H${w - c} L${w},${c} V${h} H0 Z M${w - c},0 V${c} H${w}`;
  }
  if (kind === 'decision') return `M${g(w / 2)},0 L${w},${g(h / 2)} L${g(w / 2)},${h} L0,${g(h / 2)} Z`;
  if (kind === 'terminal') {
    const r = h / 2;
    return `M${g(r)},0 H${g(w - r)} A${g(r)},${g(r)} 0 0 1 ${g(w - r)},${h} H${g(r)} A${g(r)},${g(r)} 0 0 1 ${g(r)},0 Z`;
  }
  if (kind === 'actor') {
    const hr = Math.min(w, h) / 5;
    const cx = w / 2;
    return (
      `M${g(cx - hr)},${g(hr + 2)} A${g(hr)},${g(hr)} 0 1 1 ${g(cx + hr)},${g(hr + 2)} A${g(hr)},${g(hr)} 0 1 1 ${g(cx - hr)},${g(hr + 2)} ` +
      `M${g(cx - 2.4 * hr)},${h} V${g(h - 1.6 * hr)} A${g(2.4 * hr)},${g(2 * hr)} 0 0 1 ${g(cx + 2.4 * hr)},${g(h - 1.6 * hr)} V${h}`
    );
  }
  if (kind === 'process') return `M0,0 H${w} V${h} H0 Z M6,0 V${h} M${w - 6},0 V${h}`;
  return `M0,0 H${w} V${h} H0 Z`;
}

/** Extra horizontal padding (left, right) a kind needs around its label. */
export function textInset(kind: Kind): [number, number] {
  const t: Partial<Record<Kind, [number, number]>> = {
    decision: [16, 16], terminal: [8, 8], document: [4, 12], store: [4, 4], process: [8, 8],
  };
  return t[kind] ?? [0, 0];
}
