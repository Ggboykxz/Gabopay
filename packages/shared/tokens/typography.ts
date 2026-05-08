export const typography = {
  size: {
    xs:   '11px',
    sm:   '12px',
    base: '13px',
    md:   '14px',
    lg:   '16px',
    xl:   '18px',
    '2xl':'22px',
    '3xl':'28px',
    '4xl':'36px',
    '5xl':'48px',
  },
  leading: {
    tight:  1.2,
    normal: 1.5,
    relaxed: 1.7,
  },
  tracking: {
    tight:  '-0.02em',
    normal: '0em',
    wide:   '0.05em',
    widest: '0.12em',
  },
  weight: {
    regular:  400,
    medium:   500,
    semibold: 600,
    bold:     700,
  },
} as const;

export type TypographyTokens = typeof typography;