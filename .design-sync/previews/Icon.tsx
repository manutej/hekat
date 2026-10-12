import { ICON_NAMES, Icon } from '@hekat/figtree-ds';

const row: React.CSSProperties = { display: 'flex', flexWrap: 'wrap', gap: 16, alignItems: 'center', fontFamily: 'var(--ft-font)', color: 'var(--ft-color-ink)' };

/** The whole family at 24 px with its names. */
export const Family = () => (
  <div data-preset="teaching" style={{ ...row, maxWidth: 640 }}>
    {ICON_NAMES.map((n) => (
      <div key={n} style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', width: 72, fontSize: 11, gap: 4 }}>
        <Icon name={n} size={24} title={n} />
        <span>{n}</span>
      </div>
    ))}
  </div>
);

/** One icon at the three sizes the family is designed to read at: 16, 24 and 48. */
export const Sizes = () => (
  <div data-preset="teaching" style={row}>
    <Icon name="grounder" size={16} title="grounder at 16px" />
    <Icon name="grounder" size={24} title="grounder at 24px" />
    <Icon name="grounder" size={48} title="grounder at 48px" />
    <Icon name="critic" size={16} />
    <Icon name="critic" size={24} />
    <Icon name="critic" size={48} />
    <Icon name="merge" size={16} />
    <Icon name="merge" size={24} />
    <Icon name="merge" size={48} />
  </div>
);

/** Icons follow the surrounding color: ink, accent and on a dark surface. */
export const Colors = () => (
  <div style={{ ...row }}>
    <span style={{ color: '#2B3A4A' }}><Icon name="tree" size={32} /></span>
    <span style={{ color: '#B5651D' }}><Icon name="tree" size={32} /></span>
    <span style={{ color: '#F8F9FB', background: '#1C2630', padding: 8, borderRadius: 6, display: 'inline-flex' }}><Icon name="tree" size={32} /></span>
  </div>
);
