import { useEffect } from 'react';

function useClickOutside(
  ref: React.RefObject<HTMLElement>,
  callback: () => void
) {
  const handleClickOutside = (event: MouseEvent) => {
    console.log('handleClickOutside');
    console.log('ref', ref);
    console.log('current', ref.current);
    if (ref.current && !ref.current.contains(event.target as Node)) {
      callback();
    }
  };

  useEffect(() => {
    console.log('---------------');
    console.log('ref', ref);
    console.log('callback', callback);

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [ref, callback]);
}

export { useClickOutside };
