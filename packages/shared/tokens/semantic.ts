export const semantic = {
  dark: {
    bg: {
      base:     '#0a0b0c',
      surface:  '#111214',
      elevated: '#18191c',
      overlay:  '#1e2023',
    },
    border: {
      subtle:  '#1e2023',
      default: '#2a2d31',
      strong:  '#3a3e44',
    },
    text: {
      primary:   '#f1f3f5',
      secondary: '#868e96',
      tertiary:  '#495057',
      inverse:   '#0a0b0c',
    },
    brand: {
      default:  '#009e60',
      hover:    '#007d4d',
      active:   '#005c39',
      subtle:   '#003b24',
      on:       '#e6f7ef',
    },
    status: {
      success:       '#009e60',
      successBg:     '#001a10',
      successBorder: '#003b24',
      error:         '#fa5252',
      errorBg:       '#1a0505',
      errorBorder:   '#3b1010',
      warning:       '#fcc419',
      warningBg:     '#1a1400',
      warningBorder: '#3b2e00',
      pending:       '#339af0',
      pendingBg:     '#050f1a',
      pendingBorder: '#0e2d4a',
      processing:    '#fd7e14',
      processingBg:  '#1a0a00',
      processingBorder: '#3b1f00',
    },
  },
  light: {
    bg: {
      base:     '#ffffff',
      surface:  '#f8f9fa',
      elevated: '#f1f3f5',
      overlay:  '#e9ecef',
    },
    border: {
      subtle:  '#f1f3f5',
      default: '#dee2e6',
      strong:  '#ced4da',
    },
    text: {
      primary:   '#141618',
      secondary: '#495057',
      tertiary:  '#868e96',
      inverse:   '#ffffff',
    },
    brand: {
      default:  '#009e60',
      hover:    '#007d4d',
      active:   '#005c39',
      subtle:   '#e6f7ef',
      on:       '#003b24',
    },
  },
} as const;

export type SemanticTokens = typeof semantic;