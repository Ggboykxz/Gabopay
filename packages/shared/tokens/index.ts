export const tokens = {
  color: {
    brand:   '#009e60',
    bg: {
      base:     '#0a0b0c',
      surface:  '#111214',
      elevated: '#18191c',
    },
    border: {
      subtle:  '#1e2023',
      default: '#2a2d31',
      strong:  '#3a3e44',
    },
    text: {
      primary:   '#f1f3f5',
      secondary: '#868e96',
      muted:     '#495057',
    },
    status: {
      success: '#009e60',
      error:   '#fa5252',
      warning: '#fcc419',
      pending: '#339af0',
      process: '#fd7e14',
    },
  },

  font: {
    mono:    'GeistMono, monospace',
    display: 'InterDisplay, Inter, sans-serif',
    body:    'Inter, sans-serif',
  },

  size: {
    xs: 11, sm: 12, base: 13, md: 14,
    lg: 16, xl: 18, '2xl': 22, '3xl': 28,
    '4xl': 36, '5xl': 48,
  },

  space: {
    1: 4,  2: 8,  3: 12, 4: 16,
    5: 20, 6: 24, 8: 32, 10: 40,
    12: 48, 16: 64,
  },

  radius: {
    sm: 4, md: 6, lg: 8, xl: 12, full: 9999,
  },

  shadow: {
    sm: '0 1px 2px rgba(0,0,0,0.4)',
    md: '0 4px 12px rgba(0,0,0,0.5)',
    lg: '0 8px 32px rgba(0,0,0,0.6)',
    brand: '0 0 0 3px rgba(0,158,96,0.25)',
  },

  zIndex: {
    base:    0,
    raised:  10,
    modal:   100,
    toast:   200,
    tooltip: 300,
  },
} as const;

export type Tokens = typeof tokens;