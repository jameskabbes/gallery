import colors from 'tailwindcss/colors';
import Color from 'color';

const baseColors = {
  paynes_gray: '#4f5d75',
  moss_green: '#8B9474',
  coral: '#ef8354',
};

const darken = (color: string, amount: number) =>
  Color(color).darken(amount).hex();
const lighten = (color: string, amount: number) =>
  Color(color).lighten(amount).hex();

const darkenAmount = 0.2;

export default {
  darkMode: 'class',
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: baseColors['coral'],
          darker: darken(baseColors['coral'], darkenAmount),
        },
        secondary: {
          DEFAULT: baseColors['moss_green'],
          darker: darken(baseColors['moss_green'], darkenAmount),
        },
        light: {
          darker: 'e9e9e9',
          DEFAULT: '#fafafa',
          lighter: '#ffffff',
        },
        dark: {
          darker: '#09090b',
          DEFAULT: '#18181b',
          lighter: '#363636',
        },
        textLight: colors.gray[100],
        textDark: colors.gray[900],
        success: colors.green,
        info: colors.blue,
        error: colors.red,
        warning: colors.yellow,
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
/*


--gunmetal: hsla(229, 19%, 22%, 1);
--paynes-gray: hsla(218, 19%, 38%, 1);
--silver: hsla(180, 1%, 75%, 1);
--white: hsla(0, 0%, 100%, 1);
--coral: hsla(18, 83%, 63%, 1);

$gunmetal: #2d3142ff;
$paynes-gray: #4f5d75ff;
$silver: #bfc0c0ff;
$white: #ffffffff;
$coral: #ef8354ff;

$gunmetal: hsla(229, 19%, 22%, 1);
$paynes-gray: hsla(218, 19%, 38%, 1);
$silver: hsla(180, 1%, 75%, 1);
$white: hsla(0, 0%, 100%, 1);
$coral: hsla(18, 83%, 63%, 1);

$gunmetal: rgba(45, 49, 66, 1);
$paynes-gray: rgba(79, 93, 117, 1);
$silver: rgba(191, 192, 192, 1);
$white: rgba(255, 255, 255, 1);
$coral: rgba(239, 131, 84, 1);

$gradient-top: linear-gradient(
  0deg,
  #2d3142ff,
  #4f5d75ff,
  #bfc0c0ff,
  #ffffffff,
  #ef8354ff
);
$gradient-right: linear-gradient(
  90deg,
  #2d3142ff,
  #4f5d75ff,
  #bfc0c0ff,
  #ffffffff,
  #ef8354ff
);
$gradient-bottom: linear-gradient(
  180deg,
  #2d3142ff,
  #4f5d75ff,
  #bfc0c0ff,
  #ffffffff,
  #ef8354ff
);
$gradient-left: linear-gradient(
  270deg,
  #2d3142ff,
  #4f5d75ff,
  #bfc0c0ff,
  #ffffffff,
  #ef8354ff
);
$gradient-top-right: linear-gradient(
  45deg,
  #2d3142ff,
  #4f5d75ff,
  #bfc0c0ff,
  #ffffffff,
  #ef8354ff
);
$gradient-bottom-right: linear-gradient(
  135deg,
  #2d3142ff,
  #4f5d75ff,
  #bfc0c0ff,
  #ffffffff,
  #ef8354ff
);
$gradient-top-left: linear-gradient(
  225deg,
  #2d3142ff,
  #4f5d75ff,
  #bfc0c0ff,
  #ffffffff,
  #ef8354ff
);
$gradient-bottom-left: linear-gradient(
  315deg,
  #2d3142ff,
  #4f5d75ff,
  #bfc0c0ff,
  #ffffffff,
  #ef8354ff
);
$gradient-radial: radial-gradient(
  #2d3142ff,
  #4f5d75ff,
  #bfc0c0ff,
  #ffffffff,
  #ef8354ff
);

*/
