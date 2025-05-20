import colors from 'tailwindcss/colors';
import Color from 'color';
import tailwindScrollbar from 'tailwind-scrollbar';

const baseColors = {
  paynes_gray: '#4f5d75',
  moss_green: '#8B9474',
  coral: '#ef8354',
};

const darken = (color, amount) => Color(color).darken(amount).hex();
const lighten = (color, amount) => Color(color).lighten(amount).hex();

const darkenAmount = 0.2;

const lights = {
  lighter: '#fdfdfd',
  DEFAULT: '#f5f5f5',
  darker: '#e5e5e5',
};

const darks = {
  lighter: '#404040',
  DEFAULT: '#202020',
  darker: '#101010',
};

export default {
  darkMode: 'class',
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        a: {
          bg: {
            light: lights.lighter,
            dark: darks.darker,
          },
          border: {
            light: lights.darker,
            dark: darks.lighter,
          },
          text: {
            light: darks.lighter,
            dark: lights.darker,
          },
        },
        b: {
          bg: {
            light: lights.DEFAULT,
            dark: darks.DEFAULT,
          },
          border: {
            light: lights.darker,
            dark: darks.lighter,
          },
          text: {
            light: darks.lighter,
            dark: lights.darker,
          },
        },
        light: {
          ...lights,
        },
        dark: {
          ...darks,
        },

        primary: {
          light: '#EC6A32',
          dark: '#F08456',
        },
        secondary: {
          light: '#ffffff',
          dark: '#ffffff',
        },
        success: colors.green,
        info: colors.blue,
        error: colors.red,
        warning: colors.yellow,
      },
      fontFamily: {
        sans: ['Noto Sans', 'system-ui', 'sans-serif'],
        serif: ['Merriweather', 'serif'],
        mono: ['Roboto Mono', 'monospace'],
      },
    },
  },
  plugins: [tailwindScrollbar],
};
