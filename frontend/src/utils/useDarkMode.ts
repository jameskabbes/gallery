import { useMediaQuery } from './useMediaQuery';

function useDarkMode(): boolean {
  return useMediaQuery('(prefers-color-scheme: dark)');
}

export { useDarkMode };
