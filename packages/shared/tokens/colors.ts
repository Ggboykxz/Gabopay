export const primitive = {
  green: {
    50:  '#e6f7ef',
    100: '#c3ead8',
    200: '#8fd5b2',
    300: '#5abf8c',
    400: '#2aaa6a',
    500: '#009e60',
    600: '#007d4d',
    700: '#005c39',
    800: '#003b24',
    900: '#001a10',
  },
  slate: {
    0:   '#ffffff',
    50:  '#f8f9fa',
    100: '#f1f3f5',
    200: '#e9ecef',
    300: '#dee2e6',
    400: '#ced4da',
    500: '#adb5bd',
    600: '#868e96',
    700: '#495057',
    800: '#343a40',
    900: '#212529',
    950: '#141618',
    1000:'#0a0b0c',
  },
  yellow: {
    400: '#ffd43b',
    500: '#fcc419',
    600: '#f59f00',
  },
  blue: {
    400: '#4dabf7',
    500: '#339af0',
    600: '#228be6',
  },
  red: {
    400: '#ff6b6b',
    500: '#fa5252',
    600: '#f03e3e',
  },
  orange: {
    400: '#ffa94d',
    500: '#fd7e14',
  },
} as const;

export type PrimitiveColors = typeof primitive;