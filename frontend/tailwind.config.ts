import colors from 'tailwindcss/colors';

export default {
  darkMode: 'class',
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        custom_light: {
          DEFAULT: colors.gray['200'],
          lighter: colors.gray['100'],
          darker: colors.gray['300'],
        },
        custom_dark: {
          DEFAULT: colors.gray['700'],
          lighter: colors.gray['600'],
          darker: colors.gray['800'],
        },
        primary: '#13294B',
        secondary: '#E84A27',
      },
    },
  },
  plugins: [],
};
