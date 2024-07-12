import colors from 'tailwindcss/colors';

export default {
  darkMode: 'class',
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        custom_light: {
          DEFAULT: colors.slate['200'],
          lighter: colors.slate['100'],
          darker: colors.slate['300'],
        },
        custom_dark: {
          DEFAULT: colors.slate['700'],
          lighter: colors.slate['600'],
          darker: colors.slate['800'],
        },
        primary: '#13294B',
        secondary: '#E84A27',
      },
      fontFamily: {
        sans: ['Roboto', 'system-ui', 'sans-serif'],
        serif: ['Merriweather', 'serif'],
        mono: ['Roboto Mono', 'monospace'],
      },
    },
  },
  plugins: [],
};
