/** FigTree design tokens as data, mirroring tokens.css and figtree/styles.py. */
export type PresetName = 'paper' | 'teaching' | 'slide';
export type Tone = 'attention' | 'processing' | 'residual' | 'input';

export interface Preset {
  name: PresetName;
  palette: Record<Tone | 'container' | 'border' | 'label' | 'title' | 'icon' | 'control', string>;
  font: string;
  fontSize: { label: number; annot: number; title: number; caption: number };
  stroke: { main: number; border: number };
  containerDash: string;
  radius: { block: number; container: number };
  grid: number;
  gap: { h: number; v: number; row: number };
  padding: number;
  minArrow: number;
  marker: { w: number; h: number };
}

const editorialPalette = {
  attention: '#F3C9A4', processing: '#C9DCF0', residual: '#F6EFD2', input: '#E6E8EC',
  container: '#F8F9FB', border: '#2B3A4A', label: '#1C2630', title: '#5B6B7C', icon: '#2B3A4A', control: '#9A9A9A',
};

export const PRESETS: Record<PresetName, Preset> = {
  paper: {
    name: 'paper',
    palette: {
      attention: '#D4A574', processing: '#7BA3C9', residual: '#E8D4A0', input: '#E8E8E8',
      container: '#F5F5F5', border: '#333333', label: '#333333', title: '#333333', icon: '#333333', control: '#9A9A9A',
    },
    font: '"Times New Roman", Times, serif',
    fontSize: { label: 12, annot: 10, title: 12, caption: 11 },
    stroke: { main: 1.2, border: 0.8 },
    containerDash: '4 2',
    radius: { block: 4, container: 4 },
    grid: 8,
    gap: { h: 24, v: 16, row: 48 },
    padding: 24,
    minArrow: 20,
    marker: { w: 5, h: 3.5 },
  },
  teaching: {
    name: 'teaching',
    palette: editorialPalette,
    font: '"IBM Plex Sans", "Helvetica Neue", Arial, sans-serif',
    fontSize: { label: 14, annot: 11, title: 12, caption: 13 },
    stroke: { main: 1.4, border: 1.0 },
    containerDash: '',
    radius: { block: 6, container: 10 },
    grid: 8,
    gap: { h: 40, v: 24, row: 64 },
    padding: 32,
    minArrow: 24,
    marker: { w: 8, h: 6 },
  },
  slide: {
    name: 'slide',
    palette: editorialPalette,
    font: '"IBM Plex Sans", "Helvetica Neue", Arial, sans-serif',
    fontSize: { label: 18, annot: 13, title: 14, caption: 15 },
    stroke: { main: 1.6, border: 1.2 },
    containerDash: '',
    radius: { block: 8, container: 12 },
    grid: 8,
    gap: { h: 56, v: 32, row: 80 },
    padding: 40,
    minArrow: 28,
    marker: { w: 10, h: 7 },
  },
};

/** Snap a coordinate to the 8 px grid the FigTree worker lays out on. */
export const snap = (v: number, grid = 8): number => Math.round(v / grid) * grid;
